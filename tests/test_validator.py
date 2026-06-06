import pytest
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ingestion.validator import validate_teams_df, validate_players_df, validate_stats_df

VALID_TEAMS = pd.DataFrame({
    'team_id': [1610612747, 1610612744],
    'abbreviation': ['LAL', 'GSW'],
    'full_name': ['Los Angeles Lakers', 'Golden State Warriors'],
    'city': ['Los Angeles', 'San Francisco'],
    'state': ['California', 'California']
})

VALID_PLAYERS = pd.DataFrame({
    'player_id': [2544, 201939],
    'full_name': ['LeBron James', 'Stephen Curry'],
    'is_active': [True, True]
})

VALID_STATS = pd.DataFrame({
    'player_id': [2544],
    'game_id': ['0022401001'],
    'game_date': ['2025-01-15'],
    'season': ['22024'],
    'matchup': ['LAL vs. GSW'],
    'home_away': ['home'],
    'minutes_played': [35.0],
    'points': [28],
    'rebounds': [8],
    'assists': [7],
    'steals': [1],
    'blocks': [1],
    'turnovers': [3],
    'fg_attempted': [20],
    'fg_made': [11],
    'fg3_attempted': [5],
    'fg3_made': [2],
    'ft_attempted': [6],
    'ft_made': [4]
})

def test_valid_teams_passes():
    errors = validate_teams_df(VALID_TEAMS)
    assert errors == []

def test_empty_teams_fails():
    errors = validate_teams_df(pd.DataFrame())
    assert len(errors) > 0

def test_none_teams_fails():
    errors = validate_teams_df(None)
    assert len(errors) > 0

def test_duplicate_team_ids_fails():
    df = VALID_TEAMS.copy()
    df = pd.concat([df, df])
    errors = validate_teams_df(df)
    assert any('Duplicate' in e for e in errors)

def test_valid_players_passes():
    errors = validate_players_df(VALID_PLAYERS)
    assert errors == []

def test_valid_stats_passes():
    errors = validate_stats_df(VALID_STATS, player_id=2544)
    assert errors == []

def test_negative_points_fails():
    df = VALID_STATS.copy()
    df['points'] = -5
    errors = validate_stats_df(df, player_id=2544)
    assert any('Negative points' in e for e in errors)

def test_excessive_points_fails():
    df = VALID_STATS.copy()
    df['points'] = 150
    errors = validate_stats_df(df, player_id=2544)
    assert any('high points' in e for e in errors)

def test_negative_minutes_fails():
    df = VALID_STATS.copy()
    df['minutes_played'] = -5
    errors = validate_stats_df(df, player_id=2544)
    assert any('Negative minutes' in e for e in errors)

def test_none_stats_returns_empty():
    errors = validate_stats_df(None, player_id=2544)
    assert errors == []
