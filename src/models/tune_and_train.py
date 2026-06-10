import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from dotenv import load_dotenv
from models.features import build_feature_matrix
from models.tuner import tune_hyperparameters
from models.trainer import train_model
from ingestion.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

for target in ['points', 'rebounds', 'assists']:
    logger.info(f"\n{'='*50}")
    logger.info(f"Tuning and training for: {target}")

    df, feature_cols = build_feature_matrix(engine, target=target)

    best_params, best_mae, study = tune_hyperparameters(
        df, feature_cols, target=target, n_trials=30
    )

    logger.info(f"Retraining with best params (MAE={best_mae:.3f})...")
    model, metrics = train_model(
        df, feature_cols,
        target=target,
        params=best_params
    )

    logger.info(f"Final tuned test MAE for {target}: {metrics['mae']:.3f}")

logger.info("\nAll models tuned and retrained successfully!")
