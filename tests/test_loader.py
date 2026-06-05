import pytest
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import patch, MagicMock
from ingestion.loader import load_teams, load_players, load_player_stats

SAMPLE_TEAMS_DF = pd.DataFrame({
    'team_id': [1610612747, 1610612744],
    'abbreviation': ['LAL', 'GSW'],
    'full_name': ['Los Angeles Lakers', 'Golden State Warriors'],
    'city': ['Los Angeles', 'San Francisco'],
    'state': ['California', 'California']
})

SAMPLE_PLAYERS_DF = pd.DataFrame({
    'player_id': [2544, 201939],
    'full_name': ['LeBron James', 'Stephen Curry'],
    'is_active': [True, True]
})

SAMPLE_STATS_DF = pd.DataFrame({
    'player_id': [2544, 2544],
    'game_id': ['0022401001', '0022401002'],
    'game_date': ['2025-01-15', '2025-01-13'],
    'season': ['22024', '22024'],
    'matchup': ['LAL vs. GSW', 'LAL @ BOS'],
    'home_away': ['home', 'away'],
    'minutes_played': [35.0, 32.0],
    'points': [28, 22],
    'rebounds': [8, 6],
    'assists': [7, 9],
    'steals': [1, 2],
    'blocks': [1, 0],
    'turnovers': [3, 2],
    'fg_attempted': [20, 18],
    'fg_made': [11, 9],
    'fg3_attempted': [5, 4],
    'fg3_made': [2, 1],
    'ft_attempted': [6, 4],
    'ft_made': [4, 3]
})

def make_mock_conn():
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

@patch('ingestion.loader.execute_values')
@patch('ingestion.loader.get_connection')
def test_load_teams_calls_execute(mock_get_conn, mock_exec):
    mock_conn, mock_cursor = make_mock_conn()
    mock_get_conn.return_value = mock_conn
    load_teams(SAMPLE_TEAMS_DF)
    assert mock_exec.called
    assert mock_conn.commit.called

@patch('ingestion.loader.execute_values')
@patch('ingestion.loader.get_connection')
def test_load_players_calls_execute(mock_get_conn, mock_exec):
    mock_conn, mock_cursor = make_mock_conn()
    mock_get_conn.return_value = mock_conn
    load_players(SAMPLE_PLAYERS_DF)
    assert mock_exec.called
    assert mock_conn.commit.called

@patch('ingestion.loader.execute_values')
@patch('ingestion.loader.get_connection')
def test_load_player_stats_returns_row_count(mock_get_conn, mock_exec):
    mock_conn, mock_cursor = make_mock_conn()
    mock_get_conn.return_value = mock_conn
    result = load_player_stats(SAMPLE_STATS_DF)
    assert mock_exec.called
    assert result == 2

def test_load_player_stats_handles_none():
    result = load_player_stats(None)
    assert result == 0

def test_load_player_stats_handles_empty_df():
    result = load_player_stats(pd.DataFrame())
    assert result == 0
