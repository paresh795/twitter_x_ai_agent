"""OpenAI service for interacting with the OpenAI API"""
import os
import logging
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service with API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = None
        self.logger = logging.getLogger(__name__)
        self.logger.info("OpenAI service initialized")
    
    async def ensure_initialized(self):
        """Ensure the OpenAI client is initialized"""
        if not self.client:
            self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def _make_request(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 150
    ):
        """Make a request to the OpenAI API"""
        await self.ensure_initialized()
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response
        except Exception as e:
            self.logger.error(f"OpenAI API request failed: {str(e)}")
            raise
    
    async def generate_tweet(
        self,
        topic: str,
        style: str = "engaging",
        max_length: int = 280,
        include_hashtags: bool = True,
        include_emojis: bool = True,
        reference_tweets: List[str] = None
    ) -> Dict[str, Any]:
        """Generate a tweet using OpenAI"""
        try:
            # Format reference tweets for the prompt
            examples = ""
            if reference_tweets:
                examples = "\nReference tweets for style:\n" + "\n".join(
                    f"- {tweet}" for tweet in reference_tweets[:3]
                )
            
            # Create the prompt
            prompt = f"""Generate a tweet about {topic} in a {style} style.
{examples}

Guidelines:
- Maximum length: {max_length} characters
- Include hashtags: {'Yes' if include_hashtags else 'No'}
- Include emojis: {'Yes' if include_emojis else 'No'}
- Keep the tone similar to the example tweets
- Make it engaging and authentic
- Focus on value and insights
- Be concise and impactful

Generate only the tweet text, no additional commentary."""
            
            # Make the API request
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert social media writer specializing in creating engaging, professional tweets that maintain brand voice and drive engagement."
                },
                {"role": "user", "content": prompt}
            ]
            
            response = await self._make_request(
                messages=messages,
                temperature=0.7,
                max_tokens=100
            )
            
            # Clean and validate the response
            tweet_text = response.choices[0].message.content.strip()
            tweet_text = self._clean_tweet(tweet_text)
            
            if not self._validate_tweet(tweet_text, max_length):
                raise ValueError("Generated tweet failed validation")
            
            return {
                "text": tweet_text,
                "prompt": prompt,
                "model": "gpt-3.5-turbo"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate tweet: {str(e)}")
            raise
    
    def _clean_tweet(self, tweet: str) -> str:
        """Clean and format the generated tweet"""
        # Remove any quotes or extra whitespace
        cleaned = tweet.strip().strip('"\'')
        # Ensure proper spacing after punctuation
        cleaned = cleaned.replace("..", ".").replace("..", ".")
        cleaned = cleaned.replace("!!", "!").replace("!!", "!")
        cleaned = cleaned.replace("  ", " ")
        return cleaned
    
    def _validate_tweet(self, tweet: str, max_length: int) -> bool:
        """Validate the generated tweet"""
        if not tweet:
            return False
        if len(tweet) > max_length:
            return False
        if not any(char.isalnum() for char in tweet):
            return False
        return True 