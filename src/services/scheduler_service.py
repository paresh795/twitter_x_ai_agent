"""Scheduler service for managing tweet scheduling"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from pathlib import Path

from .db_service import DBService
from .twitter_service import TwitterService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instance for job functions
_instance = None

def _post_scheduled_tweet(tweet_id: int, tweet_text: str):
    """Global function to post a scheduled tweet"""
    if _instance:
        _instance._post_tweet_impl(tweet_id, tweet_text)

def _check_pending_tweets():
    """Global function to check pending tweets"""
    if _instance:
        _instance._check_pending_impl()

class SchedulerService:
    """Service for managing tweet scheduling"""
    
    def __init__(self, twitter_service: TwitterService, db_service: DBService):
        """Initialize scheduler with services"""
        try:
            global _instance
            _instance = self
            
            self.twitter_service = twitter_service
            self.db_service = db_service
            
            # Set up job store
            jobstore_path = Path(__file__).parent.parent / "data" / "jobs.sqlite"
            jobstore_path.parent.mkdir(parents=True, exist_ok=True)
            jobstores = {
                'default': SQLAlchemyJobStore(url=f'sqlite:///{str(jobstore_path)}')
            }
            
            # Initialize scheduler with misfire grace time
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                job_defaults={
                    'misfire_grace_time': 15*60,  # 15 minutes grace time
                    'coalesce': True
                }
            )
            
            # Start scheduler
            self.scheduler.start()
            logger.info("Scheduler service initialized successfully")
            
            # Add job to check pending tweets
            self.add_check_pending_job()
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {str(e)}")
            raise Exception(f"Failed to initialize scheduler: {str(e)}")
    
    def add_check_pending_job(self):
        """Add job to check pending tweets"""
        try:
            self.scheduler.add_job(
                _check_pending_tweets,
                'interval',
                minutes=1,
                id='check_pending_tweets',
                replace_existing=True,
                max_instances=1
            )
        except Exception as e:
            logger.error(f"Failed to add check pending job: {str(e)}")
    
    def _post_tweet_impl(self, tweet_id: int, tweet_text: str):
        """Internal implementation to post a scheduled tweet"""
        try:
            # Post tweet
            response = self.twitter_service.post_tweet(tweet_text)
            
            # Update status
            self.db_service.update_tweet_status(tweet_id, 'posted')
            logger.info(f"Successfully posted scheduled tweet {tweet_id}")
            
            # Remove the job after successful posting
            job_id = f'tweet_{tweet_id}'
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
        except Exception as e:
            error_msg = str(e)
            self.db_service.update_tweet_status(tweet_id, 'failed', error_msg)
            logger.error(f"Failed to post scheduled tweet {tweet_id}: {error_msg}")
    
    def _check_pending_impl(self):
        """Internal implementation to check pending tweets"""
        try:
            pending_tweets = self.db_service.get_pending_tweets()
            for tweet in pending_tweets:
                # Only process if no active job exists
                job_id = f'tweet_{tweet["id"]}'
                if not self.scheduler.get_job(job_id):
                    self._post_tweet_impl(tweet['id'], tweet['text'])
        except Exception as e:
            logger.error(f"Error checking pending tweets: {str(e)}")
    
    def schedule_tweet(self, tweet_text: str, scheduled_time: datetime) -> int:
        """Schedule a tweet for posting"""
        try:
            # Add to database first
            tweet_id = self.db_service.add_scheduled_tweet(tweet_text, scheduled_time)
            
            # Then schedule the job
            job_id = f'tweet_{tweet_id}'
            self.scheduler.add_job(
                func=_post_scheduled_tweet,
                trigger=DateTrigger(run_date=scheduled_time, timezone='UTC'),
                args=[tweet_id, tweet_text],
                id=job_id,
                replace_existing=True,
                max_instances=1
            )
            
            logger.info(f"Scheduled tweet {tweet_id} for {scheduled_time}")
            return tweet_id
            
        except Exception as e:
            logger.error(f"Failed to schedule tweet: {str(e)}")
            raise Exception(f"Failed to schedule tweet: {str(e)}")
    
    def cancel_scheduled_tweet(self, tweet_id: int):
        """Cancel a scheduled tweet"""
        try:
            # Remove from scheduler first
            job_id = f'tweet_{tweet_id}'
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Then delete from database
            self.db_service.delete_scheduled_tweet(tweet_id)
            logger.info(f"Cancelled scheduled tweet {tweet_id}")
            
        except Exception as e:
            logger.error(f"Failed to cancel tweet: {str(e)}")
            raise Exception(f"Failed to cancel tweet: {str(e)}")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler shutdown successfully")
            global _instance
            _instance = None
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")
            raise Exception(f"Error shutting down scheduler: {str(e)}") 