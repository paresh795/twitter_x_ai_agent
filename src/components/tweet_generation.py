import streamlit as st
import asyncio
import logging
import json
from typing import Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_reference_tweets() -> list:
    """Load reference tweets from JSON file"""
    try:
        reference_file = Path(__file__).parent.parent / "data" / "reference_tweets.json"
        if reference_file.exists():
            with open(reference_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [tweet["text"] for tweet in data["tweets"]]
        logger.warning(f"Reference tweets file not found at {reference_file.absolute()}")
        return []
    except Exception as e:
        logger.error(f"Failed to load reference tweets: {str(e)}")
        return []

def render_tweet_generation():
    """Render the tweet generation interface"""
    generator = st.session_state.services.get("generator")
    twitter = st.session_state.services.get("twitter")
    
    if not generator or not twitter:
        logger.error("Required services not initialized properly")
        st.error("Required services not initialized. Please check your configuration.")
        return
    
    st.markdown("### Generate New Tweet")
    
    # Initialize session state for generated tweet if needed
    if "generated_tweet" not in st.session_state:
        st.session_state.generated_tweet = None
    if "post_success" not in st.session_state:
        st.session_state.post_success = False
    if "post_message" not in st.session_state:
        st.session_state.post_message = ""
    
    # Topic input
    topic = st.text_input(
        "Topic",
        help="Enter the topic or subject for the tweet (e.g., 'investing', 'bitcoin', 'personal finance')"
    )
    
    # Advanced options
    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            style = st.selectbox(
                "Style",
                ["Informative", "Engaging", "Professional", "Casual"],
                index=1,
                help="Select the tone and style for your tweet"
            )
            include_hashtags = st.checkbox("Include Hashtags", value=True)
        with col2:
            max_length = st.slider(
                "Maximum Length",
                min_value=50,
                max_value=280,
                value=200,
                help="Maximum length of the generated tweet"
            )
            include_emojis = st.checkbox("Include Emojis", value=True)
    
    # Generate button
    if st.button("Generate Tweet"):
        if not topic:
            st.warning("Please enter a topic for the tweet.")
            return
        
        logger.info(f"Generating tweet for topic: {topic}")
        with st.spinner("Generating tweet..."):
            try:
                # Load reference tweets
                reference_tweets = load_reference_tweets()
                if not reference_tweets:
                    st.error("No reference tweets found. Please ensure reference_tweets.json exists.")
                    return
                
                # Generate tweet
                result = asyncio.run(generator.generate_tweet(
                    topic=topic,
                    style=style.lower(),
                    max_length=max_length,
                    include_hashtags=include_hashtags,
                    include_emojis=include_emojis,
                    reference_tweets=reference_tweets
                ))
                
                # Store the generated tweet in session state
                st.session_state.generated_tweet = result
                
            except Exception as e:
                logger.error(f"Error generating tweet: {str(e)}")
                st.error(f"Error generating tweet: {str(e)}")
    
    # Show tweet preview and post button if we have a generated tweet
    if st.session_state.generated_tweet:
        st.markdown("#### Tweet Preview")
        st.markdown(f"```{st.session_state.generated_tweet['text']}```")
        
        col1, col2 = st.columns([1, 3])
        
        # Post button in first column
        with col1:
            if st.button("Post Now", key="post_tweet"):
                logger.info("Attempting to post tweet")
                try:
                    response = twitter.post_tweet(st.session_state.generated_tweet["text"])
                    logger.info(f"Tweet posted successfully: {response}")
                    
                    # Store success message in session state
                    st.session_state.post_success = True
                    st.session_state.post_message = f"Tweet posted successfully! View it [here](https://twitter.com/user/status/{response['id']})"
                    
                    # Clear the generated tweet
                    st.session_state.generated_tweet = None
                    st.rerun()
                    
                except Exception as e:
                    if "rate limit" in str(e).lower():
                        st.error("Twitter rate limit reached. Please wait a few minutes and try again.")
                    else:
                        st.error(f"Failed to post tweet: {str(e)}")
                    logger.error(f"Failed to post tweet: {str(e)}")
        
        # Schedule button in second column (placeholder for now)
        with col2:
            if st.button("Schedule for Later", key="schedule_tweet", disabled=True):
                st.info("Scheduling feature coming soon!")
    
    # Show success message if post was successful
    if st.session_state.get('post_success'):
        st.success(st.session_state.post_message)
        # Clear success state after showing
        st.session_state.post_success = False
        st.session_state.post_message = "" 