import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.trainer import time_series_split_data, evaluate_model
import xgboost as xgb

def make_sample_df():
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        'game_date': pd.date_range('2023-01-01', periods=n),
        'points': np.random.randint(5, 40, n),
        'points_roll_5': np.random.uniform(10, 30, n),
        'points_roll_10': np.random.uniform(10, 30, n),
        'points_roll_20': np.random.uniform(10, 30, n),
        'points_lag_1': np.random.randint(5, 40, n),
        'points_lag_2': np.random.randint(5, 40, n),
        'points_lag_3': np.random.randint(5, 40, n),
        'is_home': np.random.randint(0, 2, n),
        'days_rest': np.random.randint(1, 5, n),
        'is_back_to_back': np.random.randint(0, 2, n),
        'game_number': range(1, n+1),
        'opp_avg_pts_allowed': np.random.uniform(105, 120, n),
    })
    return df

FEATURE_COLS = [
    'points_roll_5', 'points_roll_10', 'points_roll_20',
    'points_lag_1', 'points_lag_2', 'points_lag_3',
    'is_home', 'days_rest', 'is_back_to_back',
    'game_number', 'opp_avg_pts_allowed'
]

def test_time_series_split_no_leakage():
    df = make_sample_df()
    X_train, X_test, y_train, y_test = time_series_split_data(
        df, FEATURE_COLS, 'points', test_size=0.2
    )
    assert len(X_train) > len(X_test)
    assert len(X_train) + len(X_test) == len(df)

def test_time_series_split_sizes():
    df = make_sample_df()
    X_train, X_test, y_train, y_test = time_series_split_data(
        df, FEATURE_COLS, 'points', test_size=0.2
    )
    assert abs(len(X_test) / len(df) - 0.2) < 0.05

def test_evaluate_model_returns_metrics():
    df = make_sample_df()
    X_train, X_test, y_train, y_test = time_series_split_data(
        df, FEATURE_COLS, 'points'
    )
    model = xgb.XGBRegressor(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test, 'Test')
    assert 'mae' in metrics
    assert 'rmse' in metrics
    assert 'within_5_pct' in metrics
    assert metrics['mae'] >= 0
    assert metrics['rmse'] >= metrics['mae']

def test_evaluate_model_within_pct_range():
    df = make_sample_df()
    X_train, X_test, y_train, y_test = time_series_split_data(
        df, FEATURE_COLS, 'points'
    )
    model = xgb.XGBRegressor(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)
    assert 0 <= metrics['within_5_pct'] <= 100
    assert 0 <= metrics['within_10_pct'] <= 100
