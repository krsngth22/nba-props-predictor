import joblib
import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.logger import get_logger
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'models')

def get_sqlalchemy_engine():
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{name}")

def load_model(target='points'):
    model_path = os.path.join(MODEL_DIR, f'xgb_{target}.joblib')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Train first.")
    artifact = joblib.load(model_path)
    logger.info(f"Loaded model for {target} (test MAE: {artifact['test_mae']:.3f})")
    return artifact

def predict_player_game(player_features: dict, target='points'):
    artifact = load_model(target)
    model = artifact['model']
    feature_cols = artifact['feature_cols']

    row = pd.DataFrame([player_features])
    for col in feature_cols:
        if col not in row.columns:
            row[col] = 0
    row = row[feature_cols].fillna(0)

    prediction = model.predict(row)[0]
    prediction = max(0, float(prediction))

    logger.info(f"Prediction for {target}: {prediction:.1f}")
    return round(prediction, 1)

def predict_from_db(engine, player_id, target='points'):
    query = f"""
        SELECT * FROM player_game_stats
        WHERE player_id = {player_id}
        ORDER BY game_date DESC
        LIMIT 20
    """
    recent_games = pd.read_sql(query, engine)

    if len(recent_games) == 0:
        raise ValueError(f"No games found for player {player_id}")

    artifact = load_model(target)
    feature_cols = artifact['feature_cols']

    features = {}
    for stat in ['points', 'rebounds', 'assists', 'minutes_played']:
        for window in [5, 10, 20]:
            col = f'{stat}_roll_{window}'
            features[col] = recent_games[stat].head(window).mean()
        for lag in [1, 2, 3]:
            col = f'{stat}_lag_{lag}'
            features[col] = recent_games[stat].iloc[lag-1] if lag <= len(recent_games) else 0

    features['is_home'] = 1
    features['days_rest'] = 2
    features['is_back_to_back'] = 0
    features['game_number'] = len(recent_games) + 1
    features['day_of_week'] = 4
    features['month'] = 11

    for col in ['fg_pct', 'fg3_pct', 'ft_pct', 'true_shooting_pct',
                'assist_turnover_ratio', 'points_per_minute']:
        features[col] = recent_games[col].mean() if col in recent_games.columns else 0

    for col in ['opp_avg_pts_allowed', 'opp_avg_reb_allowed', 'opp_avg_ast_allowed']:
        features[col] = recent_games[col].mean() if col in recent_games.columns else 110.0

    return predict_player_game(features, target)

if __name__ == "__main__":
    engine = get_sqlalchemy_engine()
    player_id = 1626164

    print(f"\nPredictions for Devin Booker (id={player_id}):")
    print("-" * 40)
    for target in ['points', 'rebounds', 'assists']:
        try:
            pred = predict_from_db(engine, player_id, target)
            print(f"  Predicted {target:<12}: {pred}")
        except Exception as e:
            print(f"  Could not predict {target}: {e}")
