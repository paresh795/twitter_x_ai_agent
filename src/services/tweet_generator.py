"""Tweet generator service for creating tweets using OpenAI"""
from typing import Dict, Any, Optional, List
import logging
from src.services.openai_service import OpenAIService

class TweetGenerator:
    """Service for generating tweets using OpenAI"""
    
    def __init__(self, openai_service: OpenAIService):
        """Initialize the tweet generator with OpenAI service"""
        self.openai_service = openai_service
        self.logger = logging.getLogger(__name__)
    
    async def generate_tweet(
        self,
        topic: str,
        style: str = "engaging",
        max_length: int = 280,
        include_hashtags: bool = True,
        include_emojis: bool = True,
        reference_tweets: List[str] = None
    ) -> Dict[str, Any]:
        """Generate a tweet based on the given parameters"""
        try:
            self.logger.info(f"Generating tweet for topic: {topic}")
            
            # Generate tweet using OpenAI
            result = await self.openai_service.generate_tweet(
                topic=topic,
                style=style,
                max_length=max_length,
                include_hashtags=include_hashtags,
                include_emojis=include_emojis,
                reference_tweets=reference_tweets
            )
            
            self.logger.info("Tweet generated successfully")
            return {
                "text": result["text"],
                "topic": topic,
                "style": style,
                "metrics": {
                    "likes": 0,
                    "retweets": 0,
                    "replies": 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate tweet: {str(e)}")
            raise 