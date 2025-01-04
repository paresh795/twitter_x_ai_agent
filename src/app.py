"""Main Streamlit application for Twitter AI Agent"""
import streamlit as st
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from src.services.openai_service import OpenAIService
from src.services.twitter_service import TwitterService
from src.services.tweet_generator import TweetGenerator
from src.components.tweet_generation import render_tweet_generation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_session_state():
    """Initialize session state variables"""
    if "services" not in st.session_state:
        st.session_state.services = {
            "openai": None,
            "twitter": None,
            "generator": None
        }
    if "generated_tweet" not in st.session_state:
        st.session_state.generated_tweet = None

def load_environment():
    """Load environment variables"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Environment variables loaded successfully")
    else:
        logger.warning("No .env file found")
        st.error("No .env file found. Please create one with your API credentials.")
        st.stop()

def initialize_services():
    """Initialize required services"""
    try:
        # Initialize OpenAI service
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            st.error("OpenAI API key not found. Please add it to your .env file.")
            return False
        
        openai_service = OpenAIService(openai_key)
        
        # Get Twitter credentials
        twitter_creds = {
            "api_key": os.getenv("TWITTER_API_KEY"),
            "api_secret": os.getenv("TWITTER_API_SECRET"),
            "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
            "access_secret": os.getenv("TWITTER_ACCESS_SECRET")
        }
        
        if not all(twitter_creds.values()):
            st.error("Twitter API credentials not found. Please add them to your .env file.")
            return False
        
        # Initialize Twitter service
        twitter_service = TwitterService(**twitter_creds)
        
        # Store services in session state
        st.session_state.services.update({
            "openai": openai_service,
            "twitter": twitter_service,
            "generator": TweetGenerator(openai_service)
        })
        
        logger.info("Services initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        st.error(f"Failed to initialize services: {str(e)}")
        return False

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Twitter AI Agent",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("Twitter AI Agent 🤖")
    
    # Initialize session state
    initialize_session_state()
    
    # Load environment variables
    load_environment()
    
    # Initialize services if needed
    if not st.session_state.services["openai"]:
        if not initialize_services():
            st.stop()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select a page",
        ["Tweet Generation"]
    )
    
    # Render selected page
    if page == "Tweet Generation":
        render_tweet_generation()

if __name__ == "__main__":
    main() 