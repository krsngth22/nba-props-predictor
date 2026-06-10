import optuna
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.logger import get_logger

logger = get_logger(__name__)

optuna.logging.set_verbosity(optuna.logging.WARNING)

def objective(trial, X, y, n_splits=5):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 500),
        'max_depth': trial.suggest_int('max_depth', 3, 8),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'gamma': trial.suggest_float('gamma', 0.0, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 1.0),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.5, 2.0),
        'random_state': 42,
    }

    tscv = TimeSeriesSplit(n_splits=n_splits)
    mae_scores = []

    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = xgb.XGBRegressor(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        preds = model.predict(X_val)
        mae_scores.append(mean_absolute_error(y_val, preds))

    return np.mean(mae_scores)

def tune_hyperparameters(df, feature_cols, target='points', n_trials=50):
    logger.info(f"Starting Optuna tuning for {target} with {n_trials} trials...")

    df = df.sort_values('game_date').reset_index(drop=True)
    X = df[feature_cols].fillna(0)
    y = df[target]

    study = optuna.create_study(
        direction='minimize',
        study_name=f'nba_{target}_tuning'
    )

    study.optimize(
        lambda trial: objective(trial, X, y),
        n_trials=n_trials,
        show_progress_bar=True
    )

    best_params = study.best_params
    best_mae = study.best_value

    logger.info(f"Best MAE for {target}: {best_mae:.3f}")
    logger.info(f"Best params: {best_params}")

    return best_params, best_mae, study

if __name__ == "__main__":
    from db import get_connection
    from models.features import build_feature_matrix
    from sqlalchemy import create_engine
    from dotenv import load_dotenv
    import os

    load_dotenv()
    engine = create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    df, feature_cols = build_feature_matrix(engine, target='points')
    best_params, best_mae, study = tune_hyperparameters(
        df, feature_cols, target='points', n_trials=30
    )
    print(f"\nBest MAE: {best_mae:.3f}")
    print(f"Best params:\n{best_params}")
