import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from src.api.database import engine
from src.api.routers import players, predictions
from src.api.deps import get_models
from src.api.schemas import HealthResponse

app = FastAPI(
    title="NBA Player Prop Predictor API",
    description="Predicts NBA player props (pts/reb/ast) using XGBoost ML models",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router)
app.include_router(predictions.router)

@app.get("/", include_in_schema=False)
def root():
    return {"message": "NBA Player Prop Predictor API", "docs": "/docs"}

@app.get("/health", response_model=HealthResponse)
def health_check():
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    models = get_models()

    return HealthResponse(
        status="ok",
        database=db_status,
        models_loaded=len(models) == 3,
        version="1.0.0"
    )
