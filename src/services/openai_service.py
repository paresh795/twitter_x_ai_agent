"""OpenAI service for generating tweets"""
import logging
import os
from typing import Dict, Any
import openai
import backoff  # For better retry handling

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self):
        """Initialize OpenAI service with API key from environment"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise Exception("OpenAI API key not found in environment variables")
            
            self.client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI service: {str(e)}")
            raise Exception(f"Failed to initialize OpenAI service: {str(e)}")
    
    @backoff.on_exception(
        backoff.expo,
        (openai.RateLimitError, openai.APIError),
        max_tries=3,
        max_time=30
    )
    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.7
    ) -> str:
        """Generate completion using OpenAI API with retry handling"""
        try:
            response = await openai.AsyncOpenAI(api_key=self.client.api_key).chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional social media expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0.6,
                frequency_penalty=0.5
            )
            
            if not response or not response.choices:
                raise Exception("Invalid response from OpenAI API")
            
            return response.choices[0].message.content.strip()
            
        except openai.RateLimitError as e:
            logger.warning(f"Rate limit hit, retrying: {str(e)}")
            raise  # Let backoff handle the retry
        except Exception as e:
            logger.error(f"Failed to generate completion: {str(e)}")
            raise Exception(f"Failed to generate completion: {str(e)}")
    
    async def generate_tweet(
        self,
        topic: str,
        style: str = "engaging",
        max_length: int = 280,
        include_hashtags: bool = True,
        include_emojis: bool = True,
        reference_tweets: list = None
    ) -> Dict[str, Any]:
        """Generate a tweet using OpenAI API"""
        try:
            # Construct the prompt
            prompt = f"Generate a {style} tweet about {topic}. "
            
            if reference_tweets:
                prompt += "Use these tweets as style reference:\n"
                for tweet in reference_tweets[:3]:  # Use up to 3 reference tweets
                    prompt += f"- {tweet}\n"
            
            prompt += f"\nRequirements:\n"
            prompt += f"- Maximum {max_length} characters\n"
            if include_hashtags:
                prompt += "- Include relevant hashtags\n"
            if include_emojis:
                prompt += "- Include relevant emojis\n"
            prompt += "- Make it engaging and shareable\n"
            prompt += "- Focus on value and insights\n"
            
            # Generate the tweet
            tweet_text = await self.generate_completion(
                prompt=prompt,
                max_tokens=max_length,
                temperature=0.8
            )
            
            # Ensure the tweet is not too long
            if len(tweet_text) > max_length:
                tweet_text = tweet_text[:max_length]
            
            logger.info("Tweet generated successfully")
            return {
                "text": tweet_text,
                "length": len(tweet_text),
                "includes_hashtags": "#" in tweet_text,
                "includes_emojis": any(c in tweet_text for c in "😀😁😂🤣😃😄😅")
            }
            
        except Exception as e:
            logger.error(f"Failed to generate tweet: {str(e)}")
            raise Exception(f"Failed to generate tweet: {str(e)}") 