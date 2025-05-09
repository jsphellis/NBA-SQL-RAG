"""
config.py

This file contains the configuration for the application.
It includes the database configuration, the OpenAI API key,
along with table information and sample data/queries.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'port': os.getenv("DB_PORT"),
    'database': os.getenv("DB_NAME"),
}

"""
Configuration for OpenAI API key
"""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

"""
Configuration for default sample limit
"""
DEFAULT_SAMPLE_LIMIT = 5

"""
Configuration for dangerous SQL keywords
"""
DANGEROUS_SQL_KEYWORDS = ['DROP', 'TRUNCATE', 'ALTER', 'GRANT', 'REVOKE']

"""
Configuration for LLM model
"""
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.1


"""
NBA schema context
"""
NBA_SCHEMA_CONTEXT = """
NBA Database Schema:

Table: players
- PERSON_ID (bigint, PRIMARY KEY): Unique identifier for each player
- FIRST_NAME (text): Player's first name
- LAST_NAME (text): Player's last name
- DISPLAY_FIRST_LAST (text): Full name in format "First Last"
- DISPLAY_LAST_COMMA_FIRST (text): Full name in format "Last, First"
- DISPLAY_FI_LAST (text): Abbreviated name format "F. Last"
- PLAYER_SLUG (text): URL-friendly name format
- BIRTHDATE (text): Date of birth
- SCHOOL (text): College or school attended
- COUNTRY (text): Country of origin
- LAST_AFFILIATION (text): Last team/school before NBA
- HEIGHT (text): Height in feet-inches format (e.g., "6-7")
- WEIGHT (double): Weight in pounds
- SEASON_EXP (bigint): Seasons of experience in NBA
- JERSEY (double): Jersey number
- POSITION (text): Player position (Guard, Forward, Center)
- ROSTERSTATUS (text): Active/Inactive status
- GAMES_PLAYED_CURRENT_SEASON_FLAG (text): Played in current season (Y/N)
- TEAM_ID (bigint): Current team identifier
- TEAM_NAME (text): Current team name
- TEAM_ABBREVIATION (text): Current team abbreviation (e.g., "LAL")
- TEAM_CODE (text): Team code
- TEAM_CITY (text): Team city
- PLAYERCODE (text): Player code
- FROM_YEAR (bigint): First year in NBA
- TO_YEAR (bigint): Last year in NBA (or current year)
- DLEAGUE_FLAG (text): G-League experience flag
- NBA_FLAG (text): NBA experience flag
- GAMES_PLAYED_FLAG (text): Has played games flag
- DRAFT_YEAR (text): Year drafted
- DRAFT_ROUND (text): Draft round
- DRAFT_NUMBER (text): Draft pick number
- GREATEST_75_FLAG (text): Named to 75 Greatest Players list

Table: teams
- TEAM_ID (bigint, PRIMARY KEY): Unique identifier for each team
- ABBREVIATION (text): Team abbreviation (e.g., "LAL")
- NICKNAME (text): Team nickname (e.g., "Lakers")
- YEARFOUNDED (bigint): Year the team was founded
- CITY (text): Team's city
- ARENA (text): Home arena name
- ARENACAPACITY (double): Arena seating capacity
- OWNER (text): Team ownership
- GENERALMANAGER (text): GM name
- HEADCOACH (text): Head coach name
- DLEAGUEAFFILIATION (text): G-League affiliate
- team_id (bigint): Duplicate of TEAM_ID
- abbreviation (text): Lowercase duplicate of ABBREVIATION
- nickname (text): Lowercase duplicate of NICKNAME
- city (text): Lowercase duplicate of CITY
- full_name (text): Full team name (City + Nickname)

Table: box_score
- GAME_ID (bigint, PRIMARY KEY): Unique game identifier
- TEAM_ID (bigint): Team identifier
- TEAM_ABBREVIATION (text): Team abbreviation
- TEAM_CITY (text): Team city
- PLAYER_ID (bigint, PRIMARY KEY): Player identifier (links to players.PERSON_ID)
- PLAYER_NAME (text): Player name
- NICKNAME (text): Player nickname
- START_POSITION (text): Starting position in game
- COMMENT (double): Comment
- MIN (text): Minutes played
- E_OFF_RATING (double): Estimated offensive rating
- OFF_RATING (double): Offensive rating
- E_DEF_RATING (double): Estimated defensive rating
- DEF_RATING (double): Defensive rating
- E_NET_RATING (double): Estimated net rating
- NET_RATING (double): Net rating
- AST_PCT (double): Assist percentage
- AST_TOV (double): Assist to turnover ratio
- AST_RATIO (double): Assist ratio
- OREB_PCT (double): Offensive rebound percentage
- DREB_PCT (double): Defensive rebound percentage
- REB_PCT (double): Rebound percentage
- TM_TOV_PCT (double): Team turnover percentage
- EFG_PCT (double): Effective field goal percentage
- TS_PCT (double): True shooting percentage
- USG_PCT (double): Usage percentage
- E_USG_PCT (double): Estimated usage percentage
- E_PACE (double): Estimated pace
- PACE (double): Pace
- PACE_PER40 (double): Pace per 40 minutes
- POSS (bigint): Possessions
- PIE (double): Player impact estimate
- FGM (double): Field goals made
- FGA (double): Field goals attempted
- FG_PCT (double): Field goal percentage
- FG3M (double): 3-point field goals made
- FG3A (double): 3-point field goals attempted
- FG3_PCT (double): 3-point field goal percentage
- FTM (double): Free throws made
- FTA (double): Free throws attempted
- FT_PCT (double): Free throw percentage
- OREB (double): Offensive rebounds
- DREB (double): Defensive rebounds
- REB (double): Total rebounds
- AST (double): Assists
- STL (double): Steals
- BLK (double): Blocks
- turnovers (double): Turnovers
- PF (double): Personal fouls
- PTS (double): Points scored
- PLUS_MINUS (double): Plus-minus statistic
- GAME_DATE (text): Date of game
- SEASON (text): Season
- SEASON_TYPE (text): Type of season (Regular, Playoffs)

Important Relationships:
1. box_score.PLAYER_ID references players.PERSON_ID (linking stats to player)
2. players.TEAM_ID references teams.TEAM_ID (linking player to team)
3. box_score.TEAM_ID references teams.TEAM_ID (linking stats to team)

Notes for SQL Queries:
- To get a player's stats, join box_score and players: ON players.PERSON_ID = box_score.PLAYER_ID
- To get team information for a player, join players and teams: ON players.TEAM_ID = teams.TEAM_ID
- For height queries, use players.HEIGHT which is in format "6-7" (feet-inches)
- Player scoring is found in box_score.PTS
- To get player names, use players.DISPLAY_FIRST_LAST, not box_score.PLAYER_NAME
- For active players filter using players.ROSTERSTATUS = 'Active'
- When working with teams, use teams.NICKNAME rather than teams.TEAM_NAME (which doesn't exist in the teams table)
"""

"""
Sample data
"""
SAMPLE_DATA = {"players": [{"PERSON_ID": 2544,
                            "FIRST_NAME": "LeBron",
                            "LAST_NAME": "James",
                            "DISPLAY_FIRST_LAST": "LeBron James",
                            "DISPLAY_LAST_COMMA_FIRST": "James, LeBron",
                            "DISPLAY_FI_LAST": "L. James",
                            "HEIGHT": "6-9",
                            "WEIGHT": 250.0,
                            "POSITION": "Forward",
                            "ROSTERSTATUS": "Active",
                            "TEAM_ID": 1610612747,
                            "TEAM_NAME": "Lakers",
                            "TEAM_ABBREVIATION": "LAL",
                            "TEAM_CITY": "Los Angeles",
                            "FROM_YEAR": 2003,
                            "TO_YEAR": 2024,
                            "DRAFT_YEAR": "2003",
                            "DRAFT_ROUND": "1",
                            "DRAFT_NUMBER": "1",
                            "GREATEST_75_FLAG": "Y"},
                           {"PERSON_ID": 201939,
                            "FIRST_NAME": "Stephen",
                            "LAST_NAME": "Curry",
                            "DISPLAY_FIRST_LAST": "Stephen Curry",
                            "DISPLAY_LAST_COMMA_FIRST": "Curry, Stephen",
                            "DISPLAY_FI_LAST": "S. Curry",
                            "HEIGHT": "6-2",
                            "WEIGHT": 185.0,
                            "POSITION": "Guard",
                            "ROSTERSTATUS": "Active",
                            "TEAM_ID": 1610612744,
                            "TEAM_NAME": "Warriors",
                            "TEAM_ABBREVIATION": "GSW",
                            "TEAM_CITY": "Golden State",
                            "FROM_YEAR": 2009,
                            "TO_YEAR": 2024,
                            "DRAFT_YEAR": "2009",
                            "DRAFT_ROUND": "1",
                            "DRAFT_NUMBER": "7",
                            "GREATEST_75_FLAG": "Y"},
                           {"PERSON_ID": 203999,
                            "FIRST_NAME": "Nikola",
                            "LAST_NAME": "Jokić",
                            "DISPLAY_FIRST_LAST": "Nikola Jokić",
                            "DISPLAY_LAST_COMMA_FIRST": "Jokić, Nikola",
                            "DISPLAY_FI_LAST": "N. Jokić",
                            "HEIGHT": "6-11",
                            "WEIGHT": 284.0,
                            "POSITION": "Center",
                            "ROSTERSTATUS": "Active",
                            "TEAM_ID": 1610612743,
                            "TEAM_NAME": "Nuggets",
                            "TEAM_ABBREVIATION": "DEN",
                            "TEAM_CITY": "Denver",
                            "FROM_YEAR": 2015,
                            "TO_YEAR": 2024,
                            "DRAFT_YEAR": "2014",
                            "DRAFT_ROUND": "2",
                            "DRAFT_NUMBER": "41",
                            "GREATEST_75_FLAG": "N"}],
               "teams": [{"TEAM_ID": 1610612747,
                          "ABBREVIATION": "LAL",
                          "NICKNAME": "Lakers",
                          "YEARFOUNDED": 1948,
                          "CITY": "Los Angeles",
                          "ARENA": "Crypto.com Arena",
                          "ARENACAPACITY": 18997.0,
                          "OWNER": "Jeanie Buss",
                          "GENERALMANAGER": "Rob Pelinka",
                          "HEADCOACH": "JJ Redick",
                          "DLEAGUEAFFILIATION": "South Bay Lakers"},
                         {"TEAM_ID": 1610612744,
                          "ABBREVIATION": "GSW",
                          "NICKNAME": "Warriors",
                          "YEARFOUNDED": 1946,
                          "CITY": "Golden State",
                          "ARENA": "Chase Center",
                          "ARENACAPACITY": 18064.0,
                          "OWNER": "Joe Lacob",
                          "GENERALMANAGER": "Mike Dunleavy Jr.",
                          "HEADCOACH": "Steve Kerr",
                          "DLEAGUEAFFILIATION": "Santa Cruz Warriors"},
                         {"TEAM_ID": 1610612743,
                          "ABBREVIATION": "DEN",
                          "NICKNAME": "Nuggets",
                          "YEARFOUNDED": 1976,
                          "CITY": "Denver",
                          "ARENA": "Ball Arena",
                          "ARENACAPACITY": 19520.0,
                          "OWNER": "Stan Kroenke",
                          "GENERALMANAGER": "Calvin Booth",
                          "HEADCOACH": "Michael Malone",
                          "DLEAGUEAFFILIATION": "Grand Rapids Gold"}],
               "box_score": [{"GAME_ID": 22301195,
                              "TEAM_ID": 1610612747,
                              "TEAM_ABBREVIATION": "LAL",
                              "TEAM_CITY": "Los Angeles",
                              "PLAYER_ID": 2544,
                              "PLAYER_NAME": "LeBron James",
                              "NICKNAME": "LeBron",
                              "START_POSITION": "F",
                              "COMMENT": 0.0,
                              "MIN": "37:41",
                              "E_OFF_RATING": 129.7,
                              "OFF_RATING": 128.4,
                              "E_DEF_RATING": 109.2,
                              "DEF_RATING": 109.0,
                              "E_NET_RATING": 20.5,
                              "NET_RATING": 19.4,
                              "AST_PCT": 0.567,
                              "AST_TOV": 4.25,
                              "AST_RATIO": 39.5,
                              "FGM": 11.0,
                              "FGA": 20.0,
                              "FG_PCT": 0.55,
                              "FG3M": 0.0,
                              "FG3A": 2.0,
                              "FG3_PCT": 0.0,
                              "FTM": 6.0,
                              "FTA": 6.0,
                              "FT_PCT": 1.0,
                              "OREB": 2.0,
                              "DREB": 9.0,
                              "REB": 11.0,
                              "AST": 17.0,
                              "STL": 5.0,
                              "BLK": 1.0,
                              "turnovers": 4.0,
                              "PF": 0.0,
                              "PTS": 28.0,
                              "PLUS_MINUS": 19.0,
                              "GAME_DATE": "2024-04-14",
                              "SEASON": "2023-24",
                              "SEASON_TYPE": "Regular Season"},
                             {"GAME_ID": 22301182,
                              "TEAM_ID": 1610612744,
                              "TEAM_ABBREVIATION": "GSW",
                              "TEAM_CITY": "Golden State",
                              "PLAYER_ID": 201939,
                              "PLAYER_NAME": "Stephen Curry",
                              "NICKNAME": "Stephen",
                              "START_POSITION": "G",
                              "COMMENT": 0.0,
                              "MIN": "32:24",
                              "E_OFF_RATING": 104.2,
                              "OFF_RATING": 104.2,
                              "E_DEF_RATING": 121.7,
                              "DEF_RATING": 115.5,
                              "E_NET_RATING": -17.5,
                              "NET_RATING": -11.3,
                              "FGM": 12.0,
                              "FGA": 23.0,
                              "FG_PCT": 0.522,
                              "FG3M": 7.0,
                              "FG3A": 13.0,
                              "FG3_PCT": 0.538,
                              "FTM": 2.0,
                              "FTA": 2.0,
                              "FT_PCT": 1.0,
                              "OREB": 0.0,
                              "DREB": 4.0,
                              "REB": 4.0,
                              "AST": 5.0,
                              "STL": 1.0,
                              "BLK": 0.0,
                              "turnovers": 7.0,
                              "PF": 2.0,
                              "PTS": 33.0,
                              "PLUS_MINUS": -8.0,
                              "GAME_DATE": "2024-04-12",
                              "SEASON": "2023-24",
                              "SEASON_TYPE": "Regular Season"},
                             {"GAME_ID": 22301164,
                              "TEAM_ID": 1610612743,
                              "TEAM_ABBREVIATION": "DEN",
                              "TEAM_CITY": "Denver",
                              "PLAYER_ID": 203999,
                              "PLAYER_NAME": "Nikola Jokić",
                              "NICKNAME": "Nikola",
                              "START_POSITION": "C",
                              "COMMENT": 0.0,
                              "MIN": "38:25",
                              "E_OFF_RATING": 128.7,
                              "OFF_RATING": 138.4,
                              "E_DEF_RATING": 129.1,
                              "DEF_RATING": 128.4,
                              "E_NET_RATING": -0.4,
                              "NET_RATING": 10.0,
                              "FGM": 16.0,
                              "FGA": 20.0,
                              "FG_PCT": 0.8,
                              "FG3M": 2.0,
                              "FG3A": 2.0,
                              "FG3_PCT": 1.0,
                              "FTM": 7.0,
                              "FTA": 12.0,
                              "FT_PCT": 0.583,
                              "OREB": 2.0,
                              "DREB": 9.0,
                              "REB": 11.0,
                              "AST": 7.0,
                              "STL": 3.0,
                              "BLK": 0.0,
                              "turnovers": 2.0,
                              "PF": 5.0,
                              "PTS": 41.0,
                              "PLUS_MINUS": 6.0,
                              "GAME_DATE": "2024-04-10",
                              "SEASON": "2023-24",
                              "SEASON_TYPE": "Regular Season"}]}

"""
Example queries
"""
EXAMPLE_QUERIES = [
    "SHOW TABLES",
    "DESCRIBE players",
    "DESCRIBE teams",
    "DESCRIBE box_score",
    "SELECT DISPLAY_FIRST_LAST, POSITION, HEIGHT FROM players LIMIT 5",
    "SELECT ABBREVIATION, NICKNAME, CITY FROM teams",
    "SELECT DISPLAY_FIRST_LAST, HEIGHT, WEIGHT, POSITION FROM players WHERE HEIGHT LIKE '7-%' ORDER BY WEIGHT DESC LIMIT 5",
    "SELECT DISPLAY_FIRST_LAST, POSITION FROM players WHERE TEAM_ID = 1610612747 LIMIT 7",
    "SELECT TEAM_NAME, COUNT(*) as player_count FROM players GROUP BY TEAM_NAME ORDER BY player_count DESC LIMIT 5",
    "SELECT POSITION, AVG(WEIGHT) as avg_weight FROM players GROUP BY POSITION",
    "SELECT players.DISPLAY_FIRST_LAST, teams.NICKNAME, teams.CITY FROM players JOIN teams ON players.TEAM_ID = teams.TEAM_ID LIMIT 10",
    "SELECT players.DISPLAY_FIRST_LAST, box_score.PTS, box_score.AST, box_score.REB FROM players JOIN box_score ON players.PERSON_ID = box_score.PLAYER_ID ORDER BY box_score.PTS DESC LIMIT 10",
    "SELECT players.DISPLAY_FIRST_LAST, teams.NICKNAME as team, AVG(box_score.PTS) as avg_points, SUM(box_score.REB) as total_rebounds FROM players JOIN box_score ON players.PERSON_ID = box_score.PLAYER_ID JOIN teams ON players.TEAM_ID = teams.TEAM_ID GROUP BY players.DISPLAY_FIRST_LAST, teams.NICKNAME ORDER BY avg_points DESC LIMIT 10",
    "SELECT teams.NICKNAME, COUNT(DISTINCT players.PERSON_ID) as num_players, AVG(box_score.PTS) as team_avg_points FROM teams JOIN players ON teams.TEAM_ID = players.TEAM_ID JOIN box_score ON players.PERSON_ID = box_score.PLAYER_ID GROUP BY teams.NICKNAME ORDER BY team_avg_points DESC LIMIT 5",
    "INSERT INTO players (PERSON_ID, FIRST_NAME, LAST_NAME, DISPLAY_FIRST_LAST, HEIGHT, WEIGHT, POSITION, TEAM_ID, TEAM_NAME, TEAM_ABBREVIATION) VALUES (20777, 'Michael', 'Jordan', 'Michael Jordan', '6-6', 216, 'Guard', 1610612741, 'Bulls', 'CHI')",
    "UPDATE players SET TEAM_ID = 1610612747, TEAM_NAME = 'Lakers', TEAM_ABBREVIATION = 'LAL', TEAM_CITY = 'Los Angeles' WHERE PERSON_ID = 20777",
    "DELETE FROM players WHERE PERSON_ID = 20777"]
