import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from ingestion.pipeline import run_pipeline
from ingestion.logger import get_logger

logger = get_logger(__name__)

def scheduled_pipeline():
    logger.info("Scheduled pipeline triggered")
    try:
        run_pipeline(max_players=50)
        logger.info("Scheduled pipeline completed successfully")
    except Exception as e:
        logger.error(f"Scheduled pipeline failed: {e}")

def start_scheduler():
    scheduler = BlockingScheduler()

    scheduler.add_job(
        scheduled_pipeline,
        trigger=CronTrigger(hour=6, minute=0),
        id='daily_pipeline',
        name='Daily NBA data pipeline',
        replace_existing=True
    )

    logger.info("Scheduler started — pipeline will run daily at 6:00 AM")
    logger.info("Press Ctrl+C to stop")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped")
        scheduler.shutdown()

if __name__ == "__main__":
    start_scheduler()
