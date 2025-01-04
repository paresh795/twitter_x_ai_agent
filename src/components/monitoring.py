import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from services import MonitoringService, TweetMetrics, PerformanceAlert

def render_monitoring_dashboard():
    """Render the monitoring dashboard with real-time metrics and alerts"""
    monitoring = st.session_state.services["monitoring"]
    
    # Performance alerts
    st.markdown("### Performance Alerts")
    alerts = monitoring.get_alerts(count=5)  # Get last 5 alerts
    
    if alerts:
        for alert in alerts:
            with st.container():
                # Alert header with color coding
                color = {
                    "high_engagement": "🟢",
                    "low_engagement": "🔴",
                    "viral_potential": "🟡"
                }.get(alert["alert_type"], "⚪")
                
                st.markdown(f"{color} **{alert['alert_type'].replace('_', ' ').title()}**")
                st.markdown(f"*{alert['message']}*")
                st.markdown(f"Tweet ID: `{alert['tweet_id']}`")
                st.markdown(f"Created: {alert['created_at']}")
                st.markdown("---")
    else:
        st.info("No recent alerts found.")
    
    # Performance trends
    st.markdown("### Performance Trends")
    
    # Time period selector for trends
    time_periods = {
        "Last 24 Hours": 1,
        "Last 7 Days": 7,
        "Last 30 Days": 30
    }
    selected_period = st.selectbox(
        "Time Period",
        list(time_periods.keys()),
        key="monitoring_period"
    )
    days = time_periods[selected_period]
    
    try:
        trends = monitoring.get_performance_trends(days=days)
        
        # Engagement metrics
        st.markdown("#### Engagement Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Average Engagement",
                f"{trends['average_engagement']:.1f}%",
                delta=None,
                help="Average engagement rate for the period"
            )
        with col2:
            st.metric(
                "Trend",
                trends["engagement_trend"],
                delta=None,
                help="Overall engagement trend"
            )
        with col3:
            top_tweets_count = len(trends["top_tweets"])
            st.metric(
                "Top Performing Tweets",
                top_tweets_count,
                delta=None,
                help="Number of high-performing tweets"
            )
        
        # Top performing tweets
        if trends["top_tweets"]:
            st.markdown("#### Top Performing Tweets")
            for tweet in trends["top_tweets"]:
                with st.expander(f"Tweet {tweet['tweet_id']} - Score: {tweet['performance_score']:.1f}"):
                    st.markdown(f"**Text:** {tweet['text']}")
                    st.markdown(f"**Created:** {tweet['created_at']}")
                    st.markdown("**Metrics:**")
                    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                    with metrics_col1:
                        st.metric("Likes", tweet["likes"])
                    with metrics_col2:
                        st.metric("Retweets", tweet["retweets"])
                    with metrics_col3:
                        st.metric("Replies", tweet["replies"])
                    with metrics_col4:
                        st.metric("Quotes", tweet["quotes"])
        
        # Performance summary
        st.markdown("#### Performance Summary")
        st.markdown(f"*{trends['performance_summary']}*")
        
    except Exception as e:
        st.error(f"Error loading performance trends: {str(e)}")
        st.exception(e)
    
    # Real-time monitoring settings
    with st.expander("Monitoring Settings"):
        st.markdown("### Alert Thresholds")
        
        col1, col2 = st.columns(2)
        with col1:
            high_engagement = st.number_input(
                "High Engagement Threshold (%)",
                min_value=0.0,
                max_value=100.0,
                value=monitoring.performance_thresholds["high_engagement"],
                step=0.1,
                help="Threshold for high engagement alerts"
            )
            
            low_engagement = st.number_input(
                "Low Engagement Threshold (%)",
                min_value=0.0,
                max_value=100.0,
                value=monitoring.performance_thresholds["low_engagement"],
                step=0.1,
                help="Threshold for low engagement alerts"
            )
        
        with col2:
            viral_potential = st.number_input(
                "Viral Potential Threshold",
                min_value=0.0,
                max_value=100.0,
                value=monitoring.performance_thresholds["viral_potential"],
                step=0.1,
                help="Threshold for viral potential alerts"
            )
        
        if st.button("Update Thresholds"):
            monitoring.performance_thresholds.update({
                "high_engagement": high_engagement,
                "low_engagement": low_engagement,
                "viral_potential": viral_potential
            })
            st.success("Monitoring thresholds updated successfully!") 