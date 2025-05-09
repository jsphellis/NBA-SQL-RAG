"""
data_clean.py

This file contains the functions for cleaning the data,
removing duplicate columns, combining data, and saving
"""
import os
import pandas as pd

def drop_duplicate_columns(df, suffixes=None):
    """
    Drops duplicate columns from a DataFrame
    """
    if suffixes:
        cols_to_keep = []
        cols_to_drop = []

        column_groups = {}
        for col in df.columns:
            has_suffix = False
            for suffix in suffixes:
                if col.endswith(suffix):
                    base_name = col[:-len(suffix)].lower()
                    has_suffix = True
                    if base_name not in column_groups:
                        column_groups[base_name] = []
                    column_groups[base_name].append(col)
                    break

            if not has_suffix:
                cols_to_keep.append(col)

        for base_name, columns in column_groups.items():
            if len(columns) > 0:
                cols_to_keep.append(columns[0])
                cols_to_drop.extend(columns[1:])
    else:
        seen_columns_lower = {}
        cols_to_keep = []
        cols_to_drop = []

        for col in df.columns:
            col_lower = col.lower()
            if col_lower in seen_columns_lower:
                cols_to_drop.append(col)
            else:
                seen_columns_lower[col_lower] = col
                cols_to_keep.append(col)

    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)

    return df


def cleanup_raw_files():
    """
    Removes the raw data files after successful processing
    """
    box_score_files = [
        '../data/box_scores/advanced_2023_24_Regular_Season.csv',
        '../data/box_scores/traditional_2023_24_Regular_Season.csv',
        '../data/box_scores/advanced_2023_24_Playoffs.csv',
        '../data/box_scores/traditional_2023_24_Playoffs.csv'
    ]
    for file in box_score_files:
        try:
            os.remove(file)
        except FileNotFoundError:
            print(f"File not found: {file}")
    try:
        os.rmdir('../data/box_scores')
    except OSError:
        print("Box scores directory not empty or already removed")

    raw_files = [
        '../data/players_detailed.csv',
        '../data/nba_teams_detailed.csv'
    ]

    for file in raw_files:
        try:
            os.remove(file)
        except FileNotFoundError:
            print(f"File not found: {file}")


def main():
    """
    Cleans the raw data files, saves cleaned data, cleans up folder
    """
    advanced_regular = pd.read_csv(
        '../data/box_scores/advanced_2023_24_Regular_Season.csv')
    traditional_regular = pd.read_csv(
        '../data/box_scores/traditional_2023_24_Regular_Season.csv')
    advanced_playoffs = pd.read_csv(
        '../data/box_scores/advanced_2023_24_Playoffs.csv')
    traditional_playoffs = pd.read_csv(
        '../data/box_scores/traditional_2023_24_Playoffs.csv')

    regular_combined = pd.merge(
        advanced_regular, traditional_regular,
        on=['GAME_ID', 'PLAYER_ID', 'GAME_DATE', 'SEASON', 'SEASON_TYPE'],
        suffixes=('_adv', '_trad')
    )

    playoffs_combined = pd.merge(
        advanced_playoffs, traditional_playoffs,
        on=['GAME_ID', 'PLAYER_ID', 'GAME_DATE', 'SEASON', 'SEASON_TYPE'],
        suffixes=('_adv', '_trad')
    )

    final_combined = pd.concat(
        [regular_combined, playoffs_combined], ignore_index=True)
    final_combined = final_combined.dropna(subset=['MIN_adv', 'MIN_trad'])

    columns_to_drop = [
        'TEAM_ID_trad',
        'TEAM_ABBREVIATION_trad',
        'TEAM_CITY_trad',
        'PLAYER_NAME_trad',
        'NICKNAME_trad',
        'START_POSITION_trad',
        'COMMENT_trad',
        'MIN_trad']

    for col in columns_to_drop:
        adv_col = final_combined[col.replace(
            '_trad', '_adv')].fillna('NaN_placeholder')
        trad_col = final_combined[col].fillna('NaN_placeholder')

        if (adv_col == trad_col).all():
            final_combined.drop(columns=[col], inplace=True)

    final_combined.columns = [
        col.replace(
            '_adv',
            '').replace(
                '_trad',
            '') for col in final_combined.columns]

    final_combined = drop_duplicate_columns(final_combined)

    final_combined.to_csv('../data/BoxScore.csv', index=False)
    print("Saved combined box score data to BoxScore.csv")

    try:
        players_detailed = pd.read_csv('../data/players_detailed.csv')
        players_detailed = drop_duplicate_columns(players_detailed)
        players_detailed.to_csv('../data/Players.csv', index=False)
        print("Saved cleaned player data to Players.csv")
    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        FileNotFoundError,
        PermissionError
    ) as e:
        print(f"Error processing player data: {e}")

    try:
        teams_detailed = pd.read_csv('../data/nba_teams_detailed.csv')
        teams_detailed = drop_duplicate_columns(teams_detailed)
        teams_detailed.to_csv('../data/Teams.csv', index=False)
        print("Saved cleaned team data to Teams.csv")
    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        FileNotFoundError,
        PermissionError
    ) as e:
        print(f"Error processing team data: {e}")

    cleanup_raw_files()
    print("Cleaned up raw data files")


if __name__ == "__main__":
    main()
