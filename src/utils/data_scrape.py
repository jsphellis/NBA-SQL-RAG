"""
data_scrape.py

This file contains the functions for scraping the data from the NBA API
"""

import os
import time
import random
import json
import shutil
import requests
import pandas as pd
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import commonplayerinfo, teamdetails, leaguegamefinder


def get_all_players(active_only=True):
    """
    Gets all players in the NBA from API
    """
    all_players = players.get_players()

    if active_only:
        all_players = [player for player in all_players if player['is_active']]

    return pd.DataFrame(all_players)


def get_detailed_player_info(players_df):
    """
    Gets detailed player info from API
    """
    detailed_file = 'src/data/players_detailed.csv'
    if os.path.exists(detailed_file):
        return pd.read_csv(detailed_file)

    detailed_players = players_df.copy()

    for col in ['height', 'weight', 'season_exp', 'jersey', 'position',
                'rosterstatus', 'team_id', 'team_name', 'from_year',
                'to_year', 'dleague_flag', 'games_played_current_season_flag',
                'draft_year', 'draft_round', 'draft_number']:
        if col not in detailed_players.columns:
            detailed_players[col] = None

    for i, (_, player) in enumerate(players_df.iterrows()):
        player_id = str(player['id'])

        try:
            player_info = commonplayerinfo.CommonPlayerInfo(
                player_id=player_id)
            player_info_df = player_info.common_player_info.get_data_frame()

            if len(player_info_df) > 0:
                for col in player_info_df.columns:
                    if col.lower() in detailed_players.columns:
                        detailed_players.loc[detailed_players['id'] == player_id, col.lower(
                        )] = player_info_df.iloc[0][col]

            time.sleep(1)

        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching player info for ID {player_id}: {e}")
            continue

    os.makedirs('src/data', exist_ok=True)
    detailed_players.to_csv(detailed_file, index=False)

    return detailed_players


def get_all_teams():
    """
    Gets all teams in the NBA from API
    """
    all_teams = teams.get_teams()
    return pd.DataFrame(all_teams)


def get_detailed_team_info(teams_df):
    """
    Gets detailed team info from API
    """
    csv_file = 'src/data/nba_teams_detailed.csv'
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)

    os.makedirs('src/data', exist_ok=True)

    all_team_info = []
    processed_ids = set()

    for i, (_, team) in enumerate(teams_df.iterrows()):
        team_id = team['id']

        if team_id in processed_ids:
            continue

        try:
            team_info = teamdetails.TeamDetails(team_id=team_id)
            team_info_df = team_info.get_data_frames()[0]

            team_info_df['team_id'] = team_id
            team_info_df['abbreviation'] = team['abbreviation']
            team_info_df['nickname'] = team['nickname']
            team_info_df['city'] = team['city']
            team_info_df['full_name'] = team['full_name']

            all_team_info.append(team_info_df)
            processed_ids.add(team_id)

            time.sleep(random.uniform(1, 2))

        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching team info for ID {team_id}: {e}")
            time.sleep(random.uniform(5, 10))
            continue

    if all_team_info:
        final_df = pd.concat(all_team_info, ignore_index=True)
        final_df.to_csv(csv_file, index=False)
        return final_df
    return None


def get_box_scores(games_df, season='2023-24', season_type='Regular Season'):
    """
    Gets box scores for all games in the NBA from API
    """
    if len(games_df) > 0:
        sample_ids = games_df['GAME_ID'].astype(str).head(5).tolist()

        if not all(str(game_id).startswith('00') for game_id in sample_ids):
            games_df['GAME_ID'] = games_df['GAME_ID'].astype(str).apply(
                lambda x: f"00{x}" if not x.startswith('00') else x
            )

    os.makedirs('src/data/box_scores', exist_ok=True)

    traditional_file = f"src/data/box_scores/traditional_{season.replace('-', '_')}_{season_type.replace(' ', '_')}.csv"
    advanced_file = f"src/data/box_scores/advanced_{season.replace('-', '_')}_{season_type.replace(' ', '_')}.csv"

    if os.path.exists(traditional_file) and os.path.exists(advanced_file):
        traditional_df = pd.read_csv(traditional_file)
        advanced_df = pd.read_csv(advanced_file)
        return traditional_df, advanced_df

    traditional_box_scores = []
    advanced_box_scores = []
    processed_games = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://www.nba.com',
        'Referer': 'https://www.nba.com/'}

    for i, (_, game) in enumerate(games_df.iterrows()):
        game_id = str(game['GAME_ID'])

        if not game_id.startswith('00'):
            game_id = f"00{game_id}"

        if game_id in processed_games:
            continue

        delay = 5 + random.uniform(0, 2)
        time.sleep(delay)

        try:
            trad_url = f"https://stats.nba.com/stats/boxscoretraditionalv2?GameID={game_id}&StartPeriod=0&EndPeriod=10&StartRange=0&EndRange=28800&RangeType=0"
            trad_response = requests.get(trad_url, headers=headers, timeout=60)

            if trad_response.status_code != 200:
                continue

            trad_data = trad_response.json()

            trad_player_stats = None
            if 'resultSets' in trad_data and isinstance(
                    trad_data['resultSets'], list):
                for result_set in trad_data['resultSets']:
                    if isinstance(result_set, dict) and result_set.get(
                            'name') == 'PlayerStats':
                        headers_list = result_set.get('headers', [])
                        rows = result_set.get('rowSet', [])
                        trad_player_stats = pd.DataFrame(
                            rows, columns=headers_list)
                        break

            if trad_player_stats is None:
                continue

            trad_player_stats['GAME_DATE'] = game.get('GAME_DATE', '')
            trad_player_stats['SEASON'] = season
            trad_player_stats['SEASON_TYPE'] = season_type

            traditional_box_scores.append(trad_player_stats)

            delay = 3 + random.uniform(0, 2)
            time.sleep(delay)

            adv_url = f"https://stats.nba.com/stats/boxscoreadvancedv2?GameID={game_id}&StartPeriod=0&EndPeriod=10&StartRange=0&EndRange=28800&RangeType=0"
            adv_response = requests.get(adv_url, headers=headers, timeout=60)

            if adv_response.status_code != 200:
                continue

            adv_data = adv_response.json()

            adv_player_stats = None
            if 'resultSets' in adv_data and isinstance(
                    adv_data['resultSets'], list):
                for result_set in adv_data['resultSets']:
                    if isinstance(result_set, dict) and result_set.get(
                            'name') == 'PlayerStats':
                        headers_list = result_set.get('headers', [])
                        rows = result_set.get('rowSet', [])
                        adv_player_stats = pd.DataFrame(
                            rows, columns=headers_list)
                        break

            if adv_player_stats is None:
                continue

            adv_player_stats['GAME_DATE'] = game.get('GAME_DATE', '')
            adv_player_stats['SEASON'] = season
            adv_player_stats['SEASON_TYPE'] = season_type

            advanced_box_scores.append(adv_player_stats)
            processed_games.append(game_id)

        except (requests.exceptions.RequestException, ValueError, KeyError, json.JSONDecodeError) as e:
            print(f"Error processing game {game_id}: {e}")
            continue

    if len(traditional_box_scores) > 0 and len(advanced_box_scores) > 0:
        traditional_df = pd.concat(traditional_box_scores, ignore_index=True)
        advanced_df = pd.concat(advanced_box_scores, ignore_index=True)

        traditional_df.to_csv(traditional_file, index=False)
        advanced_df.to_csv(advanced_file, index=False)

        return traditional_df, advanced_df
    else:
        return None, None


def main():
    """
    Main function to get all NBA data
    """
    os.makedirs('src/data', exist_ok=True)
    os.makedirs('src/data/box_scores', exist_ok=True)

    players_df = get_all_players(active_only=True)
    detailed_players_df = get_detailed_player_info(players_df)

    teams_df = get_all_teams()
    detailed_teams_df = get_detailed_team_info(teams_df)

    # Get regular season box scores
    games_df = leaguegamefinder.LeagueGameFinder(
        season_nullable='2023-24',
        season_type_nullable='Regular Season',
        league_id_nullable="00"
    ).get_data_frames()[0]

    if games_df is not None:
        get_box_scores(
            games_df,
            season='2023-24',
            season_type='Regular Season')

    playoff_games_df = leaguegamefinder.LeagueGameFinder(
        season_nullable='2023-24',
        season_type_nullable='Playoffs',
        league_id_nullable="00"
    ).get_data_frames()[0]

    if playoff_games_df is not None and len(playoff_games_df) > 0:
        get_box_scores(
            playoff_games_df,
            season='2023-24',
            season_type='Playoffs')

    temp_files = [
        'src/data/nba_players_basic.csv',
        'src/data/nba_teams_basic.csv',
        'src/data/players_detailed_partial.csv',
        'src/data/team_history',
        'src/data/games_2023_24_Regular_Season.csv',
        'src/data/games_2023_24_Playoffs.csv'
    ]

    for file in temp_files:
        if os.path.exists(file):
            if os.path.isdir(file):
                shutil.rmtree(file)
            else:
                os.remove(file)

    print("NBA data collection completed!")


if __name__ == "__main__":
    main()
