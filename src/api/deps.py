import os
import joblib
from functools import lru_cache
from sqlalchemy.orm import Session
from src.api.database import SessionLocal

MODEL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', 'data', 'models'
)

@lru_cache(maxsize=3)
def load_model(target: str):
    path = os.path.join(MODEL_DIR, f'xgb_{target}.joblib')
    if not os.path.exists(path):
        return None
    return joblib.load(path)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_models():
    models = {}
    for target in ['points', 'rebounds', 'assists']:
        artifact = load_model(target)
        if artifact:
            models[target] = artifact
    return models
