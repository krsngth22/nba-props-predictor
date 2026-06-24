import sys
sys.path.insert(0, 'src')
from ingestion.pipeline import run_pipeline
from ingestion.logger import get_logger

logger = get_logger(__name__)

logger.info("Starting full seed — all active NBA players, 2 seasons")
logger.info("This will take 1.5-2 hours. Do not close the terminal.")

stats = run_pipeline(max_players=530)

logger.info(f"Full seed complete!")
logger.info(f"Total rows loaded: {stats['rows_loaded']}")
logger.info(f"Players processed: {stats['players_processed']}")
logger.info(f"Errors: {stats['errors']}")
