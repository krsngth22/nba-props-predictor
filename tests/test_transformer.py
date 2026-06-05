import pytest
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ingestion.transformer import transform_teams, transform_players, transform_gamelog

SAMPLE_TEAMS = [
    {'id': 1610612747, 'abbreviation': 'LAL', 'full_name': 'Los Angeles Lakers', 'city': 'Los Angeles', 'state': 'California'},
    {'id': 1610612744, 'abbreviation': 'GSW', 'full_name': 'Golden State Warriors', 'city': 'San Francisco', 'state': 'California'},
]

SAMPLE_PLAYERS = [
    {'id': 2544, 'full_name': 'LeBron James', 'is_active': True},
    {'id': 201939, 'full_name': 'Stephen Curry', 'is_active': True},
]

SAMPLE_GAMELOG = pd.DataFrame({
    'Game_ID': ['0022401001', '0022401002'],
    'GAME_DATE': ['Jan 15, 2025', 'Jan 13, 2025'],
    'SEASON_ID': ['22024', '22024'],
    'MATCHUP': ['LAL vs. GSW', 'LAL @ BOS'],
    'MIN': ['35', '32'],
    'PTS': ['28', '22'],
    'REB': ['8', '6'],
    'AST': ['7', '9'],
    'STL': ['1', '2'],
    'BLK': ['1', '0'],
    'TOV': ['3', '2'],
    'FGA': ['20', '18'],
    'FGM': ['11', '9'],
    'FG3A': ['5', '4'],
    'FG3M': ['2', '1'],
    'FTA': ['6', '4'],
    'FTM': ['4', '3'],
})

def test_transform_teams_columns():
    df = transform_teams(SAMPLE_TEAMS)
    assert list(df.columns) == ['team_id', 'abbreviation', 'full_name', 'city', 'state']

def test_transform_teams_row_count():
    df = transform_teams(SAMPLE_TEAMS)
    assert len(df) == 2

def test_transform_teams_values():
    df = transform_teams(SAMPLE_TEAMS)
    assert df.iloc[0]['abbreviation'] == 'LAL'
    assert df.iloc[1]['full_name'] == 'Golden State Warriors'

def test_transform_players_columns():
    df = transform_players(SAMPLE_PLAYERS)
    assert 'player_id' in df.columns
    assert 'full_name' in df.columns
    assert 'is_active' in df.columns

def test_transform_gamelog_home_away():
    df = transform_gamelog(SAMPLE_GAMELOG, player_id=2544)
    assert df.iloc[0]['home_away'] == 'home'
    assert df.iloc[1]['home_away'] == 'away'

def test_transform_gamelog_numeric_columns():
    df = transform_gamelog(SAMPLE_GAMELOG, player_id=2544)
    assert df.iloc[0]['points'] == 28
    assert df.iloc[0]['rebounds'] == 8
    assert df.iloc[0]['assists'] == 7

def test_transform_gamelog_handles_none():
    result = transform_gamelog(None, player_id=2544)
    assert result is None

def test_transform_gamelog_handles_empty_df():
    result = transform_gamelog(pd.DataFrame(), player_id=2544)
    assert result is None
