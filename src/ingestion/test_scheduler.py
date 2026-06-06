import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from ingestion.pipeline import run_pipeline
from ingestion.logger import get_logger
import time

logger = get_logger(__name__)

def test_job():
    logger.info("Test scheduler job fired successfully")
    run_pipeline(max_players=2)
    logger.info("Test job complete")

scheduler = BackgroundScheduler()
run_time = datetime.now() + timedelta(seconds=3)

scheduler.add_job(
    test_job,
    trigger=DateTrigger(run_date=run_time),
    id='test_job'
)

scheduler.start()
logger.info(f"Scheduler started — test job will fire in 3 seconds at {run_time.strftime('%H:%M:%S')}")

time.sleep(15)
scheduler.shutdown()
logger.info("Test complete")
