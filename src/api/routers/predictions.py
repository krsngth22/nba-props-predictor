from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from src.api.deps import get_db, get_models
from src.api.schemas import PropPredictionResponse, PropPrediction
from src.api.auth import get_current_user
from src.api.cache import get_cached, set_cached

router = APIRouter(prefix="/predictions", tags=["predictions"])

def build_features_from_db(player_id: int, db: Session) -> dict:
    result = db.execute(text("""
        SELECT points, rebounds, assists, minutes_played,
               fg_made, fg_attempted, fg3_made, fg3_attempted,
               ft_made, ft_attempted, turnovers, home_away, game_date
        FROM player_game_stats
        WHERE player_id = :player_id
        ORDER BY game_date DESC
        LIMIT 20
    """), {"player_id": player_id}).fetchall()

    if not result:
        raise HTTPException(status_code=404, detail=f"No stats found for player {player_id}")

    cols = ['points','rebounds','assists','minutes_played',
            'fg_made','fg_attempted','fg3_made','fg3_attempted',
            'ft_made','ft_attempted','turnovers','home_away','game_date']
    df = pd.DataFrame(result, columns=cols)

    features = {}
    for stat in ['points', 'rebounds', 'assists', 'minutes_played', 'turnovers']:
        for window in [5, 10, 20]:
            features[f'{stat}_roll_{window}'] = df[stat].head(window).mean()
        for lag in [1, 2, 3]:
            features[f'{stat}_lag_{lag}'] = float(df[stat].iloc[lag-1]) if lag <= len(df) else 0.0

    fg_att = df['fg_attempted'].sum()
    fg3_att = df['fg3_attempted'].sum()
    ft_att = df['ft_attempted'].sum()
    pts = df['points'].sum()

    features['fg_pct'] = df['fg_made'].sum() / fg_att if fg_att > 0 else 0
    features['fg3_pct'] = df['fg3_made'].sum() / fg3_att if fg3_att > 0 else 0
    features['ft_pct'] = df['ft_made'].sum() / ft_att if ft_att > 0 else 0
    features['true_shooting_pct'] = pts / (2 * (fg_att + 0.44 * ft_att)) if (fg_att + ft_att) > 0 else 0
    features['assist_turnover_ratio'] = df['assists'].sum() / df['turnovers'].sum() if df['turnovers'].sum() > 0 else df['assists'].mean()
    features['points_per_minute'] = pts / df['minutes_played'].sum() if df['minutes_played'].sum() > 0 else 0

    features['is_home'] = 1
    features['days_rest'] = 2
    features['is_back_to_back'] = 0
    features['game_number'] = len(df) + 1
    features['day_of_week'] = 4
    features['month'] = 11
    features['opp_avg_pts_allowed'] = 110.0
    features['opp_avg_reb_allowed'] = 44.0
    features['opp_avg_ast_allowed'] = 25.0

    return features

@router.get("/{player_id}", response_model=PropPredictionResponse)
def get_player_predictions(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cache_key = f"predictions:{player_id}"
    cached = get_cached(cache_key)
    if cached:
        return PropPredictionResponse(**cached)

    player = db.execute(
        text("SELECT player_id, full_name FROM players WHERE player_id = :id"),
        {"id": player_id}
    ).fetchone()

    if not player:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")

    features = build_features_from_db(player_id, db)
    models = get_models()

    predictions = {}
    for target in ['points', 'rebounds', 'assists']:
        if target not in models:
            continue
        artifact = models[target]
        model = artifact['model']
        feature_cols = artifact['feature_cols']

        row = pd.DataFrame([features])
        for col in feature_cols:
            if col not in row.columns:
                row[col] = 0
        row = row[feature_cols].fillna(0)

        pred = float(model.predict(row)[0])
        pred = max(0, pred)

        predictions[target] = PropPrediction(
            player_id=player_id,
            full_name=player[1],
            target=target,
            predicted_value=round(pred, 1),
            model_mae=round(artifact['test_mae'], 3)
        )

    response = PropPredictionResponse(
        player_id=player_id,
        full_name=player[1],
        points=predictions.get('points'),
        rebounds=predictions.get('rebounds'),
        assists=predictions.get('assists')
    )

    set_cached(cache_key, response.model_dump())
    return response
