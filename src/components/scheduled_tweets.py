"""Component for managing scheduled tweets"""
import streamlit as st
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def render_schedule_section(tweet_data: dict):
    """Render the schedule section for a tweet"""
    if not tweet_data:
        return
    
    # Use a unique key for the container to prevent duplication
    with st.container():
        st.markdown('<div class="schedule-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📅 Schedule Tweet</div>', unsafe_allow_html=True)
        
        # Timezone selection
        timezone_utc = st.selectbox(
            "🌍 Timezone",
            ["UTC"],
            key="schedule_timezone",
            help="Currently only UTC is supported"
        )
        
        # Date and time selection
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input(
                "📆 Date",
                min_value=datetime.now(timezone.utc).date(),
                value=datetime.now(timezone.utc).date(),
                key="schedule_date"
            )
        with col2:
            time = st.time_input(
                "⏰ Time",
                value=datetime.now(timezone.utc).time(),
                key="schedule_time"
            )
        
        # Combine date and time into datetime
        scheduled_time = datetime.combine(date, time, timezone.utc)
        if scheduled_time <= datetime.now(timezone.utc):
            st.error("⚠️ Please select a future date and time")
            return
        
        # Schedule button
        if st.button("🗓️ Schedule Tweet", key="schedule_button"):
            try:
                scheduler = st.session_state.services.get("scheduler")
                if not scheduler:
                    st.error("❌ Scheduler service not initialized")
                    return
                
                logger.info(f"Scheduling tweet for {scheduled_time}")
                tweet_id = scheduler.schedule_tweet(tweet_data["text"], scheduled_time)
                
                st.markdown(
                    f'<div class="success-message">✅ Tweet scheduled successfully for {scheduled_time} UTC</div>',
                    unsafe_allow_html=True
                )
                # Clear the generated tweet to prevent duplicate scheduling
                st.session_state.generated_tweet = None
                
            except Exception as e:
                logger.error(f"Failed to schedule tweet: {str(e)}")
                st.error(f"❌ Failed to schedule tweet: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_scheduled_tweets():
    """Render the list of scheduled tweets"""
    try:
        st.markdown('<div class="section-header">📋 Scheduled Tweets</div>', unsafe_allow_html=True)
        
        db_service = st.session_state.services.get("db")
        scheduler = st.session_state.services.get("scheduler")
        
        if not db_service or not scheduler:
            st.error("❌ Required services not initialized")
            return
        
        # Get all scheduled tweets
        tweets = db_service.get_all_scheduled_tweets()
        
        if not tweets:
            st.markdown('<div class="info-box">📭 No scheduled tweets found</div>', unsafe_allow_html=True)
            return
        
        # Display tweets in a table
        for tweet in tweets:
            with st.expander(f"🕒 Tweet for {tweet['scheduled_time']}"):
                st.markdown('<div class="tweet-preview">', unsafe_allow_html=True)
                st.markdown(f'<div class="tweet-text">{tweet["tweet_text"]}</div>', unsafe_allow_html=True)
                st.markdown(f'**Status:** {tweet["status"].title()}', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if tweet['status'] == 'pending':
                    if st.button("❌ Cancel", key=f"cancel_{tweet['id']}"):
                        try:
                            scheduler.cancel_scheduled_tweet(tweet['id'])
                            st.markdown(
                                '<div class="success-message">✅ Tweet cancelled successfully</div>',
                                unsafe_allow_html=True
                            )
                        except Exception as e:
                            st.error(f"❌ Failed to cancel tweet: {str(e)}")
                
                if tweet['error_message']:
                    st.error(f"❌ Error: {tweet['error_message']}")
                    
    except Exception as e:
        logger.error(f"Error displaying scheduled tweets: {str(e)}")
        st.error(f"❌ Error displaying scheduled tweets: {str(e)}") 