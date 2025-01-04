"""Analytics component for displaying tweet performance metrics"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from src.services.analytics_service import AnalyticsService

def render_analytics_dashboard():
    """Render the analytics dashboard"""
    analytics = st.session_state.services.get("analytics")
    
    if not analytics:
        st.warning("Analytics service not initialized. Please check your configuration.")
        return
    
    st.markdown("### Tweet Analytics")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now()
        )
    
    # Get analytics data
    try:
        data = analytics.get_analytics(start_date, end_date)
        
        if not data:
            st.info("No data available for the selected date range.")
            return
        
        # Overall metrics
        st.markdown("#### Overall Performance")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Tweets",
                data["total_tweets"],
                delta=data["tweet_growth"]
            )
        with col2:
            st.metric(
                "Avg. Engagement",
                f"{data['avg_engagement']:.1f}%",
                delta=f"{data['engagement_growth']:.1f}%"
            )
        with col3:
            st.metric(
                "Total Impressions",
                data["total_impressions"],
                delta=data["impression_growth"]
            )
        with col4:
            st.metric(
                "Follower Growth",
                data["follower_growth"],
                delta=f"{data['follower_growth_rate']:.1f}%"
            )
        
        # Engagement over time
        st.markdown("#### Engagement Trends")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data["dates"],
            y=data["engagement_rates"],
            mode="lines+markers",
            name="Engagement Rate"
        ))
        fig.update_layout(
            title="Daily Engagement Rate",
            xaxis_title="Date",
            yaxis_title="Engagement Rate (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top performing tweets
        st.markdown("#### Top Performing Tweets")
        for tweet in data["top_tweets"]:
            with st.container():
                st.markdown(f"**Tweet:** {tweet['text']}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Likes", tweet["likes"])
                with col2:
                    st.metric("Retweets", tweet["retweets"])
                with col3:
                    st.metric("Replies", tweet["replies"])
                st.markdown("---")
        
    except Exception as e:
        st.error(f"Failed to load analytics: {str(e)}")
        st.exception(e) 