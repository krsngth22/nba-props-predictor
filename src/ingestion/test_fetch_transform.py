import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.fetcher import get_all_teams, get_active_players, get_player_gamelog
from ingestion.transformer import transform_teams, transform_players, transform_gamelog

print("--- Testing teams ---")
raw_teams = get_all_teams()
teams_df = transform_teams(raw_teams)
print(teams_df.head())

print("\n--- Testing players ---")
raw_players = get_active_players()
players_df = transform_players(raw_players)
print(players_df.head())

print("\n--- Testing gamelog for LeBron ---")
raw_log = get_player_gamelog(player_id=2544, season='2024-25')
gamelog_df = transform_gamelog(raw_log, player_id=2544)
print(gamelog_df[['game_date', 'matchup', 'points', 'rebounds', 'assists']].head())

print("\nAll tests passed!")
