import pandas as pd
import numpy as np
import joblib
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.logger import get_logger

logger = get_logger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'models')

def run_backtest(df, feature_cols, target='points', test_size=0.2):
    logger.info(f"Running backtest for {target}...")

    df = df.sort_values('game_date').reset_index(drop=True)
    split_idx = int(len(df) * (1 - test_size))
    test_df = df.iloc[split_idx:].copy()

    artifact = joblib.load(os.path.join(MODEL_DIR, f'xgb_{target}.joblib'))
    model = artifact['model']

    X_test = test_df[feature_cols].fillna(0)
    test_df['predicted'] = model.predict(X_test)
    test_df['predicted'] = test_df['predicted'].clip(lower=0)
    test_df['error'] = test_df['predicted'] - test_df[target]
    test_df['abs_error'] = test_df['error'].abs()

    lines = test_df[target].mean()
    test_df['prop_line'] = lines
    test_df['bet_over'] = test_df['predicted'] > test_df['prop_line']
    test_df['actual_over'] = test_df[target] > test_df['prop_line']
    test_df['correct_bet'] = test_df['bet_over'] == test_df['actual_over']

    mae = test_df['abs_error'].mean()
    rmse = np.sqrt((test_df['error'] ** 2).mean())
    within_3 = (test_df['abs_error'] <= 3).mean() * 100
    within_5 = (test_df['abs_error'] <= 5).mean() * 100
    within_10 = (test_df['abs_error'] <= 10).mean() * 100
    bet_accuracy = test_df['correct_bet'].mean() * 100

    results = {
        'target': target,
        'test_games': len(test_df),
        'mae': round(mae, 3),
        'rmse': round(rmse, 3),
        'within_3': round(within_3, 1),
        'within_5': round(within_5, 1),
        'within_10': round(within_10, 1),
        'bet_accuracy': round(bet_accuracy, 1)
    }

    logger.info(f"Backtest results for {target}:")
    logger.info(f"  Test games    : {results['test_games']}")
    logger.info(f"  MAE           : {results['mae']}")
    logger.info(f"  RMSE          : {results['rmse']}")
    logger.info(f"  Within 3      : {results['within_3']}%")
    logger.info(f"  Within 5      : {results['within_5']}%")
    logger.info(f"  Within 10     : {results['within_10']}%")
    logger.info(f"  Bet accuracy  : {results['bet_accuracy']}%")

    return results, test_df

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from dotenv import load_dotenv
    from models.features import build_feature_matrix

    load_dotenv()
    engine = create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    print("\n" + "=" * 55)
    print("BACKTEST RESULTS")
    print("=" * 55)

    for target in ['points', 'rebounds', 'assists']:
        df, feature_cols = build_feature_matrix(engine, target=target)
        results, _ = run_backtest(df, feature_cols, target=target)
        print(f"\n{target.upper()}")
        print(f"  MAE           : {results['mae']}")
        print(f"  Within 3      : {results['within_3']}%")
        print(f"  Within 5      : {results['within_5']}%")
        print(f"  Within 10     : {results['within_10']}%")
        print(f"  Bet accuracy  : {results['bet_accuracy']}%")

    print("\n" + "=" * 55)
