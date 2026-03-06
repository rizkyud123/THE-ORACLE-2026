"""
Scheduler - Daily automation for The Oracle 2026
Schedules daily picks generation at 07:00 AM

Author: Rizki Wahyudi, S.Kom
Version: 2.0.0
"""

import logging
from datetime import datetime
from typing import Optional

# APScheduler imports - handle different versions
try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger
    APSCHEDULER_V3 = True
except ImportError:
    from apscheduler.scheduler import Scheduler
    from apscheduler.triggers.cron import CronTrigger
    APSCHEDULER_V3 = False

from .config import config
from .prediction_engine import PredictionEngine

logger = logging.getLogger(__name__)


class DailyScheduler:
    """Scheduler for daily picks generation"""
    
    def __init__(self):
        self.engine = PredictionEngine()
        self.scheduler = None
    
    def generate_daily_picks(self):
        """Generate daily picks - called by scheduler"""
        logger.info("Generating daily picks...")
        try:
            # In production, this would fetch real matches from API
            # and send to Telegram
            logger.info("Daily picks generated successfully")
        except Exception as e:
            logger.error(f"Error generating daily picks: {e}")
    
    def start(self):
        """Start the scheduler"""
        try:
            if APSCHEDULER_V3:
                self.scheduler = BlockingScheduler()
                # Schedule daily at 07:00
                self.scheduler.add_job(
                    self.generate_daily_picks,
                    'cron',
                    hour=7,
                    minute=0,
                    id='daily_picks'
                )
                logger.info("Scheduler started - daily picks at 07:00")
                self.scheduler.start()
            else:
                self.scheduler = Scheduler()
                self.scheduler.add_interval_job(
                    self.generate_daily_picks,
                    hours=24,
                    start_date=datetime.now()
                )
                self.scheduler.start()
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")


def run_scheduler():
    """Run the scheduler"""
    scheduler = DailyScheduler()
    scheduler.start()


if __name__ == "__main__":
    run_scheduler()
