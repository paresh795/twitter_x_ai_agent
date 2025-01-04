import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# API Keys and Tokens
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Twitter OAuth 2.0 Credentials
TWITTER_CLIENT_ID = os.getenv('TWITTER_CLIENT_ID')
TWITTER_CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET')

# Twitter OAuth 1.0a Credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')

# Twitter App-only Authentication
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# System Configuration
MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', 300))  # 5 minutes default
RETRY_ATTEMPTS = int(os.getenv('RETRY_ATTEMPTS', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 60))  # 1 minute default

# Paths
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
REFERENCE_TWEETS_FILE = BASE_DIR / 'reference_tweets.json'

# Ensure required directories exist
LOG_DIR.mkdir(exist_ok=True) 