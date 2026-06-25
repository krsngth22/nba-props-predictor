import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from src.api.database import engine
from src.api.routers import players, predictions
from src.api.routers.auth import router as auth_router
from src.api.deps import get_models
from src.api.schemas import HealthResponse
from src.api.cache import get_cache_stats

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="NBA Player Prop Predictor API",
    description="Predicts NBA player props (pts/reb/ast) using XGBoost ML models",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(players.router)
app.include_router(predictions.router)

@app.get("/", include_in_schema=False)
def root():
    return {"message": "NBA Player Prop Predictor API", "docs": "/docs"}

@app.get("/health", response_model=HealthResponse)
@limiter.limit("30/minute")
def health_check(request: Request):
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    models = get_models()
    cache_stats = get_cache_stats()

    return HealthResponse(
        status="ok",
        database=db_status,
        models_loaded=len(models) == 3,
        version="1.0.0"
    )
