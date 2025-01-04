"""Main application module for Twitter AI Agent"""
import streamlit as st
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from src.config import load_css
from src.services.openai_service import OpenAIService
from src.services.twitter_service import TwitterService
from src.services.tweet_generator import TweetGenerator
from src.services.db_service import DBService
from src.services.scheduler_service import SchedulerService
from src.components.tweet_generation import render_tweet_generation
from src.components.scheduled_tweets import render_scheduled_tweets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables"""
    try:
        # Load .env file if it exists
        env_path = Path(__file__).parent.parent / ".env"
        if not env_path.exists():
            st.error("❌ Missing .env file. Please check the documentation for setup instructions.")
            st.stop()
        
        load_dotenv(env_path)
        
        # Verify required environment variables
        required_vars = [
            "OPENAI_API_KEY",
            "TWITTER_API_KEY",
            "TWITTER_API_SECRET",
            "TWITTER_ACCESS_TOKEN",
            "TWITTER_ACCESS_SECRET"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            st.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            st.stop()
            
        logger.info("Environment variables loaded successfully")
    except Exception as e:
        logger.error(f"Error loading environment: {str(e)}")
        st.error(f"❌ Error loading environment: {str(e)}")
        st.stop()

def initialize_services():
    """Initialize application services"""
    try:
        # Initialize OpenAI service
        openai_service = OpenAIService()
        logger.info("OpenAI service initialized")
        
        # Initialize Twitter service
        twitter_service = TwitterService()
        
        # Initialize tweet generator
        tweet_generator = TweetGenerator(openai_service)
        
        # Initialize database service
        db_service = DBService()
        
        # Initialize scheduler service
        scheduler_service = SchedulerService(twitter_service, db_service)
        
        # Store services in session state
        st.session_state.services = {
            "openai": openai_service,
            "twitter": twitter_service,
            "generator": tweet_generator,
            "db": db_service,
            "scheduler": scheduler_service
        }
        
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        st.error(f"❌ Error initializing services: {str(e)}")
        st.stop()

def main():
    """Main application entry point"""
    try:
        # Set page config
        st.set_page_config(
            page_title="Twitter AI Agent",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Load custom CSS
        load_css()
        
        # Load environment variables
        load_environment()
        
        # Initialize services if not already initialized
        if "services" not in st.session_state:
            initialize_services()
        
        # Render main components
        render_tweet_generation()
        
        # Add some spacing
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Render scheduled tweets section
        render_scheduled_tweets()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"❌ Application error: {str(e)}")

if __name__ == "__main__":
    main() 