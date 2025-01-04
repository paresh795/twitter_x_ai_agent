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
    # Clear any stale state on page load
    if "page_load" not in st.session_state:
        st.session_state.page_load = True
        st.session_state.generated_tweet = None
        st.session_state.generating = False
        st.session_state.generation_error = None
    
    generator = st.session_state.services.get("generator")
    twitter = st.session_state.services.get("twitter")
    
    if not generator or not twitter:
        logger.error("Required services not initialized properly")
        st.error("Required services not initialized. Please check your configuration.")
        return
    
    # Apply custom CSS
    st.markdown("""
        <div class="main-title">
            Twitter AI Agent <span class="main-title-icon">🤖</span>
        </div>
        <div class="subtitle">
            Generate and schedule engaging tweets powered by AI
        </div>
    """, unsafe_allow_html=True)
    
    # Create a container for the main content
    with st.container():
        st.markdown('<div class="section-header">Generate New Tweet</div>', unsafe_allow_html=True)
        
        # Topic input with improved styling
        topic = st.text_input(
            "Topic",
            key="tweet_topic",
            help="Enter the topic or subject for the tweet (e.g., 'investing', 'bitcoin', 'personal finance')",
            placeholder="Enter your topic here..."
        )
        
        # Advanced options in a styled container
        with st.expander("✨ Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                style = st.selectbox(
                    "Tweet Style",
                    ["Informative", "Engaging", "Professional", "Casual"],
                    index=1,
                    key="tweet_style",
                    help="Select the tone and style for your tweet"
                )
                include_hashtags = st.checkbox("Include Hashtags", value=True, key="tweet_hashtags")
            with col2:
                max_length = st.slider(
                    "Maximum Length",
                    min_value=50,
                    max_value=280,
                    value=200,
                    key="tweet_length",
                    help="Maximum length of the generated tweet"
                )
                include_emojis = st.checkbox("Include Emojis", value=True, key="tweet_emojis")
        
        # Generate button with loading state
        generate_clicked = st.button(
            "✨ Generate Tweet",
            key="generate_button",
            disabled=st.session_state.generating,
            help="Click to generate a new tweet"
        )
        
        # Handle generation
        if generate_clicked:
            if not topic:
                st.warning("⚠️ Please enter a topic for the tweet.")
                return
            
            st.session_state.generating = True
            st.session_state.generation_error = None
            st.session_state.generated_tweet = None
            
            try:
                # Load reference tweets
                reference_tweets = load_reference_tweets()
                if not reference_tweets:
                    st.error("❌ No reference tweets found. Please ensure reference_tweets.json exists.")
                    st.session_state.generating = False
                    return
                
                # Generate tweet with styled spinner
                with st.spinner("🤖 Crafting your tweet..."):
                    result = asyncio.run(generator.generate_tweet(
                        topic=topic,
                        style=style.lower(),
                        max_length=max_length,
                        include_hashtags=include_hashtags,
                        include_emojis=include_emojis,
                        reference_tweets=reference_tweets
                    ))
                    
                    if result:
                        st.session_state.generated_tweet = result
                    else:
                        raise Exception("Failed to generate tweet: No result returned")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error generating tweet: {error_msg}")
                st.session_state.generation_error = error_msg
            
            finally:
                st.session_state.generating = False
                st.rerun()  # Force a clean rerun after state changes
        
        # Show error if any
        if st.session_state.generation_error:
            st.error(f"❌ Error generating tweet: {st.session_state.generation_error}")
            if "rate limit" in st.session_state.generation_error.lower():
                st.info("⏳ Please wait a few seconds and try again.")
        
        # Show tweet preview and post button if we have a generated tweet
        if st.session_state.generated_tweet:
            st.markdown('<div class="tweet-preview">', unsafe_allow_html=True)
            st.markdown("#### 📝 Tweet Preview")
            st.markdown(f'<div class="tweet-text">{st.session_state.generated_tweet["text"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            
            # Post button in first column
            with col1:
                if st.button("🚀 Post Now", key="post_tweet"):
                    logger.info("Attempting to post tweet")
                    try:
                        response = twitter.post_tweet(st.session_state.generated_tweet["text"])
                        logger.info(f"Tweet posted successfully: {response}")
                        
                        # Update success message with animation
                        st.markdown(
                            f'<div class="success-message">✅ Tweet posted successfully! '
                            f'<a href="https://twitter.com/user/status/{response["id"]}" target="_blank">View it here</a></div>',
                            unsafe_allow_html=True
                        )
                        
                        # Clear the generated tweet
                        st.session_state.generated_tweet = None
                        st.rerun()  # Force a clean rerun after posting
                        
                    except Exception as e:
                        error_msg = str(e)
                        if "rate limit" in error_msg.lower():
                            st.error("⏳ Twitter rate limit reached. Please wait a few minutes and try again.")
                        else:
                            st.error(f"❌ Failed to post tweet: {error_msg}")
                        logger.error(f"Failed to post tweet: {error_msg}")
            
            # Schedule section in second column with improved styling
            with col2:
                from src.components.scheduled_tweets import render_schedule_section
                render_schedule_section(st.session_state.generated_tweet) 