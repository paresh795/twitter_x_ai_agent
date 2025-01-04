"""Database service for managing scheduled tweets"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBService:
    """Service for managing SQLite database operations"""
    
    def __init__(self):
        """Initialize database connection and create tables if needed"""
        try:
            # Get database path
            db_path = Path(__file__).parent.parent / "data" / "scheduled_tweets.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize database
            self.db_path = str(db_path)
            self._create_tables()
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise Exception(f"Failed to initialize database: {str(e)}")
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create scheduled tweets table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scheduled_tweets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tweet_text TEXT NOT NULL,
                        scheduled_time DATETIME NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        posted_at DATETIME,
                        error_message TEXT
                    )
                """)
                conn.commit()
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise Exception(f"Failed to create tables: {str(e)}")
    
    def add_scheduled_tweet(self, tweet_text: str, scheduled_time: datetime) -> int:
        """Add a new scheduled tweet to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO scheduled_tweets (tweet_text, scheduled_time)
                    VALUES (?, ?)
                    """,
                    (tweet_text, scheduled_time.isoformat())
                )
                tweet_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Added scheduled tweet with ID: {tweet_id}")
                return tweet_id
                
        except Exception as e:
            logger.error(f"Failed to add scheduled tweet: {str(e)}")
            raise Exception(f"Failed to add scheduled tweet: {str(e)}")
    
    def get_pending_tweets(self) -> List[Dict[str, Any]]:
        """Get all pending tweets that are due for posting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    """
                    SELECT * FROM scheduled_tweets
                    WHERE status = 'pending'
                    AND scheduled_time <= datetime('now')
                    ORDER BY scheduled_time ASC
                    """
                )
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get pending tweets: {str(e)}")
            raise Exception(f"Failed to get pending tweets: {str(e)}")
    
    def update_tweet_status(self, tweet_id: int, status: str, error_message: Optional[str] = None):
        """Update the status of a scheduled tweet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if status == 'posted':
                    cursor.execute(
                        """
                        UPDATE scheduled_tweets
                        SET status = ?, posted_at = datetime('now')
                        WHERE id = ?
                        """,
                        (status, tweet_id)
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE scheduled_tweets
                        SET status = ?, error_message = ?
                        WHERE id = ?
                        """,
                        (status, error_message, tweet_id)
                    )
                
                conn.commit()
                logger.info(f"Updated tweet {tweet_id} status to {status}")
                
        except Exception as e:
            logger.error(f"Failed to update tweet status: {str(e)}")
            raise Exception(f"Failed to update tweet status: {str(e)}")
    
    def get_all_scheduled_tweets(self) -> List[Dict[str, Any]]:
        """Get all scheduled tweets for display"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    """
                    SELECT * FROM scheduled_tweets
                    ORDER BY scheduled_time DESC
                    LIMIT 100
                    """
                )
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get scheduled tweets: {str(e)}")
            raise Exception(f"Failed to get scheduled tweets: {str(e)}")
    
    def delete_scheduled_tweet(self, tweet_id: int):
        """Delete a scheduled tweet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM scheduled_tweets WHERE id = ?",
                    (tweet_id,)
                )
                conn.commit()
                logger.info(f"Deleted scheduled tweet {tweet_id}")
                
        except Exception as e:
            logger.error(f"Failed to delete scheduled tweet: {str(e)}")
            raise Exception(f"Failed to delete scheduled tweet: {str(e)}") 