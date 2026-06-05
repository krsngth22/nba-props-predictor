import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import patch, MagicMock
from ingestion.fetcher import get_all_teams, get_active_players, get_player_gamelog

def test_get_all_teams_returns_list():
    teams = get_all_teams()
    assert isinstance(teams, list)
    assert len(teams) == 30
    assert 'id' in teams[0]
    assert 'full_name' in teams[0]
    assert 'abbreviation' in teams[0]

def test_get_active_players_returns_list():
    players = get_active_players()
    assert isinstance(players, list)
    assert len(players) > 0
    assert 'id' in players[0]
    assert 'full_name' in players[0]

def test_get_player_gamelog_returns_dataframe():
    df = get_player_gamelog(player_id=2544, season='2024-25')
    assert df is not None
    assert len(df) > 0
    assert 'PTS' in df.columns
    assert 'REB' in df.columns
    assert 'AST' in df.columns

def test_get_player_gamelog_retries_on_failure():
    call_count = 0
    original_import = __import__

    with patch('ingestion.fetcher.playergamelog.PlayerGameLog') as mock_gamelog:
        mock_instance = MagicMock()
        mock_instance.get_data_frames.return_value = [MagicMock()]
        mock_gamelog.side_effect = [Exception("API Error"), mock_instance]

        with patch('ingestion.fetcher.time.sleep'):
            result = get_player_gamelog(player_id=2544, season='2024-25', retries=2)

def test_get_player_gamelog_returns_none_after_all_retries():
    with patch('ingestion.fetcher.playergamelog.PlayerGameLog') as mock_gamelog:
        mock_gamelog.side_effect = Exception("API always fails")
        with patch('ingestion.fetcher.time.sleep'):
            result = get_player_gamelog(player_id=9999999, season='2024-25', retries=3)
            assert result is None
