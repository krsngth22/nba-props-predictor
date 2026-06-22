from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class PlayerBase(BaseModel):
    player_id: int
    full_name: str
    is_active: bool

class PlayerResponse(PlayerBase):
    class Config:
        from_attributes = True

class GameStatResponse(BaseModel):
    game_date: date
    matchup: str
    home_away: str
    points: int
    rebounds: int
    assists: int
    minutes_played: float
    opponent_abbr: Optional[str] = None

    class Config:
        from_attributes = True

class PropPrediction(BaseModel):
    player_id: int
    full_name: str
    target: str
    predicted_value: float
    model_mae: float

class PropPredictionResponse(BaseModel):
    player_id: int
    full_name: str
    points: Optional[PropPrediction] = None
    rebounds: Optional[PropPrediction] = None
    assists: Optional[PropPrediction] = None

class HealthResponse(BaseModel):
    status: str
    database: str
    models_loaded: bool
    version: str

class ShapFeature(BaseModel):
    feature: str
    shap_value: float
    value: float

class ShapResponse(BaseModel):
    player_id: int
    full_name: str
    target: str
    prediction: float
    features: List[ShapFeature]
