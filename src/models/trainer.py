import pandas as pd
import numpy as np
import joblib
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mlflow
import mlflow.xgboost
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error
from ingestion.logger import get_logger

logger = get_logger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def time_series_split_data(df, feature_cols, target, test_size=0.2):
    df = df.sort_values('game_date').reset_index(drop=True)
    split_idx = int(len(df) * (1 - test_size))
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    X_train = train_df[feature_cols].fillna(0)
    y_train = train_df[target]
    X_test = test_df[feature_cols].fillna(0)
    y_test = test_df[target]
    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    return X_train, X_test, y_train, y_test

def evaluate_model(model, X, y, split_name=''):
    preds = model.predict(X)
    mae = mean_absolute_error(y, preds)
    rmse = np.sqrt(mean_squared_error(y, preds))
    within_5 = np.mean(np.abs(preds - y) <= 5) * 100
    within_10 = np.mean(np.abs(preds - y) <= 10) * 100
    logger.info(f"{split_name} MAE: {mae:.3f}")
    logger.info(f"{split_name} RMSE: {rmse:.3f}")
    logger.info(f"{split_name} Within 5 pts: {within_5:.1f}%")
    logger.info(f"{split_name} Within 10 pts: {within_10:.1f}%")
    return {
        'mae': mae,
        'rmse': rmse,
        'within_5_pct': within_5,
        'within_10_pct': within_10
    }

def cross_validate(df, feature_cols, target, params, n_splits=5):
    logger.info(f"Running {n_splits}-fold time series cross-validation...")
    df = df.sort_values('game_date').reset_index(drop=True)
    X = df[feature_cols].fillna(0)
    y = df[target]

    tscv = TimeSeriesSplit(n_splits=n_splits)
    mae_scores = []
    rmse_scores = []

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = xgb.XGBRegressor(**params, random_state=42)
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

        preds = model.predict(X_val)
        mae = mean_absolute_error(y_val, preds)
        rmse = np.sqrt(mean_squared_error(y_val, preds))
        mae_scores.append(mae)
        rmse_scores.append(rmse)
        logger.info(f"  Fold {fold+1}: MAE={mae:.3f}, RMSE={rmse:.3f}")

    cv_mae = np.mean(mae_scores)
    cv_rmse = np.mean(rmse_scores)
    logger.info(f"CV Mean MAE: {cv_mae:.3f} ± {np.std(mae_scores):.3f}")
    logger.info(f"CV Mean RMSE: {cv_rmse:.3f} ± {np.std(rmse_scores):.3f}")
    return cv_mae, cv_rmse

def train_model(df, feature_cols, target='points', experiment_name='nba-props'):
    logger.info(f"Training model for target: {target}")

    mlflow.set_experiment(experiment_name)

    params = {
        'n_estimators': 300,
        'max_depth': 5,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'min_child_weight': 3,
        'gamma': 0.1,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
    }

    X_train, X_test, y_train, y_test = time_series_split_data(
        df, feature_cols, target
    )

    cv_mae, cv_rmse = cross_validate(df, feature_cols, target, params)

    with mlflow.start_run(run_name=f"{target}_xgboost"):
        mlflow.log_params(params)
        mlflow.log_param('target', target)
        mlflow.log_param('n_features', len(feature_cols))
        mlflow.log_param('train_size', len(X_train))
        mlflow.log_param('test_size', len(X_test))
        mlflow.log_metric('cv_mae', cv_mae)
        mlflow.log_metric('cv_rmse', cv_rmse)

        model = xgb.XGBRegressor(**params, random_state=42)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=50
        )

        train_metrics = evaluate_model(model, X_train, y_train, 'Train')
        test_metrics = evaluate_model(model, X_test, y_test, 'Test')

        for k, v in train_metrics.items():
            mlflow.log_metric(f'train_{k}', v)
        for k, v in test_metrics.items():
            mlflow.log_metric(f'test_{k}', v)

        mlflow.xgboost.log_model(model, f"model_{target}")

        model_path = os.path.join(MODEL_DIR, f'xgb_{target}.joblib')
        joblib.dump({
            'model': model,
            'feature_cols': feature_cols,
            'target': target,
            'test_mae': test_metrics['mae'],
            'test_rmse': test_metrics['rmse']
        }, model_path)

        logger.info(f"Model saved to {model_path}")
        logger.info(f"Test MAE: {test_metrics['mae']:.3f}")
        logger.info(f"Test RMSE: {test_metrics['rmse']:.3f}")

    return model, test_metrics

if __name__ == "__main__":
    from db import get_connection
    from models.features import build_feature_matrix

    conn = get_connection()

    for target in ['points', 'rebounds', 'assists']:
        logger.info(f"\n{'='*50}")
        logger.info(f"Training model for: {target}")
        df, feature_cols = build_feature_matrix(conn, target=target)
        model, metrics = train_model(df, feature_cols, target=target)
        logger.info(f"Final test MAE for {target}: {metrics['mae']:.3f}")
