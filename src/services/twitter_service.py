"""Twitter service for interacting with the Twitter API v2"""
import logging
from typing import Dict, Any
import tweepy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterService:
    """Service for interacting with Twitter API v2"""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str = None,
        access_secret: str = None
    ):
        """Initialize Twitter service with credentials"""
        try:
            # Initialize the client with API v2 endpoints
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret,
                wait_on_rate_limit=True
            )
            logger.info("Twitter service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter service: {str(e)}")
            raise Exception(f"Failed to initialize Twitter service: {str(e)}")
    
    def post_tweet(self, text: str) -> Dict[str, Any]:
        """Post a tweet using Twitter API v2"""
        try:
            logger.info(f"Attempting to post tweet: {text}")
            response = self.client.create_tweet(text=text)
            
            # The response from create_tweet() is a Response object
            # The actual tweet data is in response.data
            if not response or not response.data:
                raise Exception("Invalid response from Twitter API")
            
            tweet_data = response.data
            
            result = {
                "id": str(tweet_data["id"]),  # Access as dictionary
                "text": tweet_data["text"]    # Access as dictionary
            }
            logger.info(f"Tweet posted successfully with id: {result['id']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to post tweet: {str(e)}")
            raise Exception(f"Failed to post tweet: {str(e)}")
    
    def get_me(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        try:
            response = self.client.get_me()
            if not response or not hasattr(response, 'data'):
                raise Exception("Failed to get user information")
            
            return {
                "id": str(response.data.id),
                "username": response.data.username,
                "name": response.data.name
            }
        except Exception as e:
            logger.error(f"Failed to get user info: {str(e)}")
            raise Exception(f"Failed to get user info: {str(e)}") 