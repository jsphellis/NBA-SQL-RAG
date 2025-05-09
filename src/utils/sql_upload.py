"""
sql_upload.py

This file contains the functions for uploading the NBA database to a MySQL server
"""

import os
import sys
from dotenv import load_dotenv
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, exc as sqlalchemy_exc
from src.utils.config import DB_CONFIG

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

TABLE_DATA = {
    'teams': os.path.join(DATA_DIR, 'nba_teams_detailed.csv'),
    'players': os.path.join(DATA_DIR, 'nba_players_detailed.csv'),
    'box_score': os.path.join(DATA_DIR, 'box_scores_2023_24.csv')
}


def validate_file_paths():
    """
    Check if all required CSV files exist before proceeding
    """
    all_files_exist = True

    print("Validating CSV file locations...")
    for table_name, file_path in TABLE_DATA.items():
        if os.path.exists(file_path):
            print(f"{table_name} file exists: {os.path.basename(file_path)}")
        else:
            print(f"{table_name} file missing: {file_path}")
            print(f" Absolute path: {os.path.abspath(file_path)}")
            all_files_exist = False

    if not all_files_exist:
        print("\nERROR: One or more required CSV files are missing")
        print("Please ensure all CSV files are in the correct location")
        return False

    print("All CSV files found successfully")
    return True


def drop_all_tables():
    """
    Drops all existing tables in the NBA database
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        if not tables:
            print("No existing tables to drop.")
            cursor.close()
            conn.close()
            return True

        print(f"Found {len(tables)} tables to drop:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                print(f"  Dropped table: {table_name}")
            except mysql.connector.Error as e:
                print(f"  Error dropping table {table_name}: {e}")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()

        cursor.close()
        conn.close()
        print("Successfully dropped all existing tables.")
        return True

    except mysql.connector.Error as e:
        print(f"Error dropping tables: {e}")
        return False


def add_keys_and_relationships():
    """
    Adds primary keys and foreign key (if possible)relationships to tables
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("\nSetting up primary keys and relationships...")

        cursor.execute("""
            ALTER TABLE teams
            ADD PRIMARY KEY (TEAM_ID)
        """)
        print("Added primary key to teams (TEAM_ID)")

        cursor.execute("""
            ALTER TABLE players
            ADD PRIMARY KEY (PERSON_ID)
        """)
        print("Added primary key to players (PERSON_ID)")

        cursor.execute("""
            ALTER TABLE box_score
            ADD PRIMARY KEY (GAME_ID, PLAYER_ID)
        """)
        print("Added composite primary key to box_score (GAME_ID, PLAYER_ID)")

        try:
            cursor.execute("""
                ALTER TABLE players
                ADD CONSTRAINT fk_players_teams
                FOREIGN KEY (TEAM_ID) REFERENCES teams(TEAM_ID)
                ON DELETE CASCADE
                ON UPDATE CASCADE
            """)
            print("Added foreign key: players.TEAM_ID -> teams.TEAM_ID")
        except mysql.connector.Error as e:
            print(
                f"Warning: Could not add foreign key from players to teams: {e}")
            print("  This could be due to missing references or data inconsistencies")

        try:
            cursor.execute("""
                ALTER TABLE box_score
                ADD CONSTRAINT fk_boxscore_players
                FOREIGN KEY (PLAYER_ID) REFERENCES players(PERSON_ID)
                ON DELETE CASCADE
                ON UPDATE CASCADE
            """)
            print("Added foreign key: box_score.PLAYER_ID -> players.PERSON_ID")
        except mysql.connector.Error as e:
            print(
                f"Warning: Could not add foreign key from box_score to players: {e}")
            print("  This could be due to missing references or data inconsistencies")

        try:
            cursor.execute("""
                ALTER TABLE box_score
                ADD CONSTRAINT fk_boxscore_teams
                FOREIGN KEY (TEAM_ID) REFERENCES teams(TEAM_ID)
                ON DELETE CASCADE
                ON UPDATE CASCADE
            """)
            print("Added foreign key: box_score.TEAM_ID -> teams.TEAM_ID")
        except mysql.connector.Error as e:
            print(
                f"Warning: Could not add foreign key from box_score to teams: {e}")
            print("  This could be due to missing references or data inconsistencies")

        conn.commit()
        cursor.close()
        conn.close()

        print("Successfully added all primary keys and foreign key relationships!")
        return True

    except mysql.connector.Error as e:
        print(f"Error adding keys and relationships: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


def create_database():
    """
    Creates a new MySQL database and tables using pandas
    """
    if not validate_file_paths():
        print("Exiting due to missing files.")
        return False

    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        cursor = conn.cursor()

        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"Database '{DB_CONFIG['database']}' created or already exists")

        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL server: {e}")
        return False

    if not drop_all_tables():
        print("Failed to drop existing tables. Aborting.")
        return False

    try:
        connection_str = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        engine = create_engine(connection_str)
    except sqlalchemy_exc.SQLAlchemyError as e:
        print(f"Error creating SQLAlchemy engine: {e}")
        return False

    dfs = {}
    for table_name, csv_file in TABLE_DATA.items():
        try:
            print(
                f"\nLoading {table_name} data from {os.path.basename(csv_file)}...")
            df = pd.read_csv(csv_file)
            print(f"Read {len(df)} rows from {os.path.basename(csv_file)}")

            original_columns = list(df.columns)
            uppercase_columns = [
                col for col in original_columns if col.isupper() or col.upper() == col]

            if table_name == 'players' and 'PERSON_ID' not in uppercase_columns:
                person_id_candidates = [
                    col for col in uppercase_columns if 'ID' in col]
                if person_id_candidates:
                    df = df.rename(
                        columns={
                            person_id_candidates[0]: 'PERSON_ID'})
                    uppercase_columns = list(df.columns)
                    print(
                        f"Renamed {person_id_candidates[0]} to PERSON_ID for consistency")

            dropped_columns = [
                col for col in original_columns if col not in uppercase_columns]
            if dropped_columns:
                df = df[uppercase_columns]
                print(
                    f"Dropped {len(dropped_columns)} non-uppercase columns to avoid duplicates")

            if 'TO' in df.columns:
                df = df.rename(columns={'TO': 'TURNOVERS'})

            if table_name == 'teams' and 'TEAM_ID' in df.columns:
                df = df.drop_duplicates(subset=['TEAM_ID'], keep='first')

            if table_name == 'players' and 'PERSON_ID' in df.columns:
                df = df.drop_duplicates(subset=['PERSON_ID'], keep='first')

            if table_name == 'box_score' and 'GAME_ID' in df.columns and 'PLAYER_ID' in df.columns:
                original_count = len(df)
                df = df.drop_duplicates(
                    subset=[
                        'GAME_ID',
                        'PLAYER_ID'],
                    keep='first')
                duplicate_count = original_count - len(df)

                if duplicate_count > 0:
                    print(f"""
                        Removed {duplicate_count} duplicate rows from box_score (duplicate GAME_ID, PLAYER_ID combinations)
                    """)

            dfs[table_name] = df

        except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            print(f"Error processing {table_name}: {e}")
            return False

    try:
        if 'players' in dfs and 'teams' in dfs:
            players_df = dfs['players']
            teams_df = dfs['teams']

            if 'TEAM_ID' in players_df and 'TEAM_ID' in teams_df and 'TEAM_NAME' in teams_df and 'TEAM_NAME' in players_df:
                print("""
                    \nFinding mismatches between players and teams:
                """)

                valid_team_ids = set(teams_df['TEAM_ID'].unique())
                invalid_team_ids_mask = ~players_df['TEAM_ID'].isin(
                    valid_team_ids)
                invalid_count = invalid_team_ids_mask.sum()

                if invalid_count > 0:
                    print(f"""
                        Found {invalid_count} players with invalid TEAM_ID references
                    """)

                    team_name_to_id = dict(
                        zip(teams_df['TEAM_NAME'], teams_df['TEAM_ID']))

                    fixed_count = 0
                    for idx in players_df[invalid_team_ids_mask].index:
                        player_team_name = players_df.loc[idx, 'TEAM_NAME']
                        if player_team_name in team_name_to_id:
                            players_df.loc[idx,
                                           'TEAM_ID'] = team_name_to_id[player_team_name]
                            fixed_count += 1

                    print(f"""
                        Fixed {fixed_count} players by matching team names
                    """)

                    remaining_invalid = ~players_df['TEAM_ID'].isin(
                        valid_team_ids)
                    if remaining_invalid.sum() > 0:
                        players_df = players_df[~remaining_invalid]
                        print(f"""
                            Removed {remaining_invalid.sum()} players with unresolvable team references
                        """)

                dfs['players'] = players_df

        if 'box_score' in dfs and 'players' in dfs:
            box_score_df = dfs['box_score']
            players_df = dfs['players']

            if 'PLAYER_ID' in box_score_df and 'PERSON_ID' in players_df and 'PLAYER_NAME' in box_score_df and 'PLAYER_NAME' in players_df:
                print("""
                    \nFinding mismatches between box_score and players:
                """)

                valid_player_ids = set(players_df['PERSON_ID'].unique())
                invalid_player_ids_mask = ~box_score_df['PLAYER_ID'].isin(
                    valid_player_ids)
                invalid_count = invalid_player_ids_mask.sum()

                if invalid_count > 0:
                    print(f"""
                        Found {invalid_count} box score entries with invalid PLAYER_ID references
                    """)

                    player_name_to_id = dict(
                        zip(players_df['PLAYER_NAME'], players_df['PERSON_ID']))

                    fixed_count = 0
                    for idx in box_score_df[invalid_player_ids_mask].index:
                        box_score_player_name = box_score_df.loc[idx,
                                                                 'PLAYER_NAME']
                        if box_score_player_name in player_name_to_id:
                            box_score_df.loc[idx,
                                             'PLAYER_ID'] = player_name_to_id[box_score_player_name]
                            fixed_count += 1

                    print(f"""
                        Fixed {fixed_count} box score entries by matching player names
                    """)

                    remaining_invalid = ~box_score_df['PLAYER_ID'].isin(
                        valid_player_ids)
                    if remaining_invalid.sum() > 0:
                        box_score_df = box_score_df[~remaining_invalid]
                        print(f"""
                            Removed {remaining_invalid.sum()} box score entries with unresolvable player references
                        """)

                dfs['box_score'] = box_score_df

        if 'box_score' in dfs and 'teams' in dfs:
            box_score_df = dfs['box_score']
            teams_df = dfs['teams']

            if 'TEAM_ID' in box_score_df and 'TEAM_ID' in teams_df and 'TEAM_ABBREVIATION' in box_score_df and 'ABBREVIATION' in teams_df:
                print("""
                    \nFinding mismatches between box_score and teams:
                """)

                valid_team_ids = set(teams_df['TEAM_ID'].unique())
                invalid_team_ids_mask = ~box_score_df['TEAM_ID'].isin(
                    valid_team_ids)
                invalid_count = invalid_team_ids_mask.sum()

                if invalid_count > 0:
                    print(f"""
                        Found {invalid_count} box score entries with invalid TEAM_ID references
                    """)

                    team_abbrev_to_id = dict(
                        zip(teams_df['ABBREVIATION'], teams_df['TEAM_ID']))
                    team_city_to_id = dict(
                        zip(teams_df['CITY'], teams_df['TEAM_ID']))

                    fixed_count = 0
                    for idx in box_score_df[invalid_team_ids_mask].index:
                        team_abbrev = box_score_df.loc[idx,
                                                       'TEAM_ABBREVIATION']
                        team_city = box_score_df.loc[idx,
                                                     'TEAM_CITY'] if 'TEAM_CITY' in box_score_df.columns else None

                        if team_abbrev in team_abbrev_to_id:
                            box_score_df.loc[idx,
                                             'TEAM_ID'] = team_abbrev_to_id[team_abbrev]
                            fixed_count += 1
                        elif team_city and team_city in team_city_to_id:
                            box_score_df.loc[idx,
                                             'TEAM_ID'] = team_city_to_id[team_city]
                            fixed_count += 1

                    print(f"""
                        Fixed {fixed_count} box score entries by matching team abbreviation or city
                    """)

                    remaining_invalid = ~box_score_df['TEAM_ID'].isin(
                        valid_team_ids)
                    if remaining_invalid.sum() > 0:
                        box_score_df = box_score_df[~remaining_invalid]
                        print(
                            f"""
                            Removed {remaining_invalid.sum()} box score entries with unresolvable team references
                        """)

                dfs['box_score'] = box_score_df

    except (ValueError, KeyError) as e:
        print(f"Error while fixing data inconsistencies: {e}")
        return False

    table_order = ['teams', 'players', 'box_score']

    for table_name in table_order:
        if table_name in dfs:
            df = dfs[table_name]
            try:
                print(
                    f"\nSaving {table_name} table to database ({len(df)} rows)...")

                df.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists='replace',
                    index=False,
                    chunksize=1000
                )
                print(
                    f"Table {table_name} created with {len(df)} rows and {len(df.columns)} columns")
            except sqlalchemy_exc.SQLAlchemyError as e:
                print(f"Error saving {table_name} to database: {e}")
                return False

    if not add_keys_and_relationships():
        print("Certain keys and relationships not added, but database created successfully")
        return False

    print("\nDatabase setup complete with all relationships!")
    return True


def connect_to_db():
    """
    Establishes a connection to the MySQL NBA database
    """
    return mysql.connector.connect(**DB_CONFIG)


def example_query():
    """
    Example function demonstrating how to query the database
    """
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database.")
            return

        print("\nTables in database:")

        for table in tables:
            print(f"- {table[0]}")

            print("\nRow counts:")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  - {table_name}: {count} rows")

                print("\nColumns in each table:")
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                    columns = cursor.fetchall()
                    print(f"  - {table_name}: {len(columns)} columns")
                    for i, col in enumerate(columns[:5]):
                        print(f"    - {col[0]} ({col[1]})")
                    if len(columns) > 5:
                        print(f"    - ... and {len(columns) - 5} more columns")

                print("\nForeign key relationships:")
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"""
                        SELECT
                            TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME,
                            REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                        FROM
                            INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                        WHERE
                            REFERENCED_TABLE_SCHEMA = '{DB_CONFIG['database']}' AND
                            TABLE_NAME = '{table_name}'
                    """)
                    fks = cursor.fetchall()

                    cursor.execute(f"""
                        SELECT
                            TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME,
                            REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                        FROM
                            INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                        WHERE
                            REFERENCED_TABLE_SCHEMA = '{DB_CONFIG['database']}' AND
                            REFERENCED_TABLE_NAME = '{table_name}'
                    """)

                    referenced_fks = cursor.fetchall()

                    if fks:
                        for fk in fks:
                            print(
                                f"  - {fk[0]}.{fk[1]} → {fk[3]}.{fk[4]} (via {fk[2]})")

                    if referenced_fks:
                        for fk in referenced_fks:
                            print(
                                f"  - {fk[0]}.{fk[1]} → {fk[3]}.{fk[4]} (via {fk[2]})")

        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        print(f"Error querying database: {e}")


if __name__ == "__main__":
    SUCCESS = create_database()
    if SUCCESS:
        example_query()
    else:
        print("Database creation failed. See errors above.")
        sys.exit(1)
