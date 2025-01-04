from typing import Dict, List, Optional, Any
import json
import logging
import os
import asyncio
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from .services import OpenAIService, TweetGenerator, TwitterService

class TwitterAIAgent:
    def __init__(self):
        self.setup_logging()
        self.reference_data = None
        self.openai_service = None
        self.tweet_generator = None
        self.twitter_service = None

    def setup_logging(self) -> None:
        """Configure logging with rotation and proper formatting"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "twitter_ai_agent.log"
        handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5
        )
        
        # Set the handler's level to INFO
        handler.setLevel(logging.INFO)
        
        # Create logger with name
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)  # Set logger level to INFO
        
        # Set format for the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(handler)
        self.logger.addHandler(logging.StreamHandler())
        
        self.logger.info("Logging system initialized")

    def load_reference_data(self) -> Dict[str, Any]:
        """Load reference tweets from JSON file"""
        try:
            reference_file = Path(__file__).parent / "data" / "reference_tweets.json"
            if not reference_file.exists():
                self.logger.error("Reference tweets file not found")
                raise FileNotFoundError("Reference tweets file not found")
                
            with open(reference_file, 'r', encoding='utf-8') as file:
                self.reference_data = json.load(file)
                self.logger.info("Reference data loaded successfully")
                return self.reference_data
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing reference tweets: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error loading reference data: {e}")
            raise

    async def setup_openai(self, api_key: str) -> None:
        """Initialize OpenAI service with validation"""
        try:
            if not api_key or not isinstance(api_key, str) or len(api_key.strip()) == 0:
                raise ValueError("Invalid API key provided")
            
            self.openai_service = OpenAIService(api_key)
            # Wait for API key validation
            await self.openai_service.ensure_initialized()
            
            # Initialize tweet generator after OpenAI service is ready
            self.tweet_generator = TweetGenerator(self.openai_service)
            
            self.logger.info("OpenAI service and tweet generator initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI service: {e}")
            self.openai_service = None
            self.tweet_generator = None
            raise ValueError(f"OpenAI initialization failed: {str(e)}")

    def setup_twitter(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_secret: str
    ) -> None:
        """Initialize Twitter service with credentials"""
        try:
            self.twitter_service = TwitterService(
                api_key=api_key,
                api_secret=api_secret,
                access_token=access_token,
                access_secret=access_secret
            )
            
            self.logger.info("Twitter service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter service: {e}")
            self.twitter_service = None
            raise ValueError(f"Twitter initialization failed: {str(e)}")

    async def generate_tweet(
        self,
        topic: str,
        style: str = "engaging",
        max_length: int = 280,
        include_hashtags: bool = True,
        include_emojis: bool = True
    ) -> Dict[str, Any]:
        """Generate a tweet about a specific topic"""
        if not self.tweet_generator:
            raise RuntimeError("Tweet generator not initialized")
            
        try:
            # Load reference tweets
            if not self.reference_data:
                self.load_reference_data()
            
            reference_tweets = [tweet["text"] for tweet in self.reference_data["tweets"]]
            
            # Generate the tweet
            result = await self.tweet_generator.generate_tweet(
                topic=topic,
                style=style,
                max_length=max_length,
                include_hashtags=include_hashtags,
                include_emojis=include_emojis,
                reference_tweets=reference_tweets
            )
            
            self.logger.info(f"Generated tweet for topic: {topic}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to generate tweet: {e}")
            raise

    def post_tweet(self, text: str) -> Dict[str, Any]:
        """Post a tweet"""
        if not self.twitter_service:
            raise RuntimeError("Twitter service not initialized")
            
        try:
            # Post to Twitter
            result = self.twitter_service.post_tweet(text)
            
            self.logger.info(f"Successfully posted tweet: {result['id']}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to post tweet: {e}")
            raise

    def get_mentions(self, since_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get mentions since the last checked ID"""
        if not self.twitter_service:
            raise RuntimeError("Twitter service not initialized")
            
        try:
            mentions = self.twitter_service.get_mentions(since_id)
            self.logger.info(f"Retrieved {len(mentions)} mentions")
            return mentions
        except Exception as e:
            self.logger.error(f"Failed to get mentions: {e}")
            raise

    def initialize_system(self):
        """Initialize all system components"""
        try:
            self.logger.info("Initializing system...")
            
            # Load reference data
            self.load_reference_data()
            
            # Initialize OpenAI service
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            asyncio.run(self.setup_openai(openai_api_key))
            
            # Initialize Twitter service
            twitter_creds = {
                "api_key": os.getenv("TWITTER_API_KEY"),
                "api_secret": os.getenv("TWITTER_API_SECRET"),
                "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
                "access_secret": os.getenv("TWITTER_ACCESS_SECRET")
            }
            
            if not all(twitter_creds.values()):
                raise ValueError("Missing Twitter API credentials in environment variables")
                
            self.setup_twitter(**twitter_creds)
            
            self.logger.info("System initialization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            raise

async def main():
    """Main entry point for the Twitter AI Agent"""
    agent = TwitterAIAgent()
    await agent.initialize_system()
    return agent

if __name__ == "__main__":
    asyncio.run(main()) 