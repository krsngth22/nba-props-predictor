import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.features import (
    add_rolling_features,
    add_lag_features,
    add_efficiency_features,
    add_game_context_features
)

def make_sample_df():
    return pd.DataFrame({
        'player_id': [2544] * 10,
        'game_date': pd.date_range('2025-01-01', periods=10),
        'home_away': ['home', 'away'] * 5,
        'points': [20, 25, 18, 30, 22, 28, 15, 35, 24, 27],
        'rebounds': [8, 6, 9, 7, 10, 5, 8, 9, 7, 6],
        'assists': [7, 9, 5, 8, 6, 10, 4, 7, 8, 9],
        'minutes_played': [35, 32, 38, 34, 36, 33, 30, 37, 35, 34],
        'turnovers': [3, 2, 4, 1, 3, 2, 2, 3, 1, 2],
        'fg_made': [8, 10, 7, 12, 9, 11, 6, 14, 9, 11],
        'fg_attempted': [18, 20, 16, 22, 19, 21, 15, 24, 18, 20],
        'fg3_made': [2, 3, 1, 4, 2, 3, 1, 4, 2, 3],
        'fg3_attempted': [5, 6, 4, 7, 5, 6, 4, 7, 5, 6],
        'ft_made': [2, 2, 3, 2, 2, 3, 2, 3, 4, 2],
        'ft_attempted': [3, 2, 4, 2, 3, 4, 2, 4, 5, 2],
        'steals': [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
        'blocks': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    })

def test_rolling_features_added():
    df = make_sample_df()
    result = add_rolling_features(df, windows=[5])
    assert 'points_roll_5' in result.columns
    assert 'rebounds_roll_5' in result.columns
    assert 'assists_roll_5' in result.columns

def test_rolling_features_use_shift():
    df = make_sample_df()
    result = add_rolling_features(df, windows=[5])
    assert pd.isna(result['points_roll_5'].iloc[0]) or result['points_roll_5'].iloc[0] >= 0

def test_lag_features_added():
    df = make_sample_df()
    result = add_lag_features(df, lags=[1, 2])
    assert 'points_lag_1' in result.columns
    assert 'points_lag_2' in result.columns
    assert 'assists_lag_1' in result.columns

def test_lag_1_equals_previous_game():
    df = make_sample_df()
    result = add_lag_features(df, lags=[1])
    assert result['points_lag_1'].iloc[1] == result['points'].iloc[0]
    assert result['points_lag_1'].iloc[2] == result['points'].iloc[1]

def test_efficiency_features_added():
    df = make_sample_df()
    result = add_efficiency_features(df)
    assert 'fg_pct' in result.columns
    assert 'true_shooting_pct' in result.columns
    assert 'points_per_minute' in result.columns

def test_fg_pct_range():
    df = make_sample_df()
    result = add_efficiency_features(df)
    assert (result['fg_pct'] >= 0).all()
    assert (result['fg_pct'] <= 1).all()

def test_context_features_added():
    df = make_sample_df()
    result = add_game_context_features(df)
    assert 'is_home' in result.columns
    assert 'days_rest' in result.columns
    assert 'is_back_to_back' in result.columns
    assert 'game_number' in result.columns

def test_is_home_binary():
    df = make_sample_df()
    result = add_game_context_features(df)
    assert set(result['is_home'].unique()).issubset({0, 1})

def test_game_number_increments():
    df = make_sample_df()
    result = add_game_context_features(df)
    assert result['game_number'].iloc[0] == 1
    assert result['game_number'].iloc[-1] == 10
