from typing import Dict, List, Any, Optional, Tuple
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from dataclasses import dataclass
from .monitoring_service import TweetMetrics

@dataclass
class AnalyticsSummary:
    """Data class for analytics summary"""
    period_start: str
    period_end: str
    total_tweets: int
    total_engagement: int
    avg_engagement_rate: float
    engagement_trend: str
    top_performing_tweets: List[Dict[str, Any]]
    engagement_by_hour: Dict[str, float]
    content_performance: Dict[str, float]

class AnalyticsService:
    def __init__(self, monitoring_service):
        """Initialize analytics service"""
        self.logger = logging.getLogger(__name__)
        self.monitoring_service = monitoring_service
        
    def generate_analytics_report(self, days: int = 30) -> AnalyticsSummary:
        """Generate comprehensive analytics report"""
        try:
            # Get recent metrics
            metrics = self._get_recent_metrics(days)
            
            if not metrics:
                return self._generate_empty_summary(days)
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame([vars(m) for m in metrics])
            
            # Calculate period bounds
            period_start = df['created_at'].min()
            period_end = df['created_at'].max()
            
            # Basic metrics
            total_tweets = len(df)
            total_engagement = df['total_engagement'].sum()
            avg_engagement = df['engagement_rate'].mean()
            
            # Get top performing tweets
            top_tweets = df.nlargest(5, 'performance_score')[
                ['tweet_id', 'text', 'performance_score', 'total_engagement']
            ].to_dict('records')
            
            # Analyze engagement by hour
            df['hour'] = pd.to_datetime(df['created_at']).dt.hour
            engagement_by_hour = df.groupby('hour')['engagement_rate'].mean().to_dict()
            
            # Analyze content performance (based on common hashtags/keywords)
            content_performance = self._analyze_content_performance(df)
            
            # Calculate engagement trend
            df['created_at_dt'] = pd.to_datetime(df['created_at'])
            df = df.sort_values('created_at_dt')
            if len(df) > 1:
                first_half = df['engagement_rate'][:len(df)//2].mean()
                second_half = df['engagement_rate'][len(df)//2:].mean()
                if abs(second_half - first_half) < 0.1 * first_half:  # 10% threshold
                    trend = "stable"
                else:
                    trend = "increasing" if second_half > first_half else "decreasing"
            else:
                trend = "stable"
            
            return AnalyticsSummary(
                period_start=period_start,
                period_end=period_end,
                total_tweets=total_tweets,
                total_engagement=total_engagement,
                avg_engagement_rate=avg_engagement,
                engagement_trend=trend,
                top_performing_tweets=top_tweets,
                engagement_by_hour=engagement_by_hour,
                content_performance=content_performance
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate analytics report: {e}")
            raise
    
    def get_optimal_posting_times(self) -> List[Dict[str, Any]]:
        """Determine optimal posting times based on historical performance"""
        try:
            metrics = self.monitoring_service.metrics_history
            
            if not metrics:
                return []
            
            # Convert to DataFrame
            df = pd.DataFrame([vars(m) for m in metrics])
            df['hour'] = pd.to_datetime(df['created_at']).dt.hour
            
            # Calculate average engagement by hour
            hourly_engagement = df.groupby('hour').agg({
                'engagement_rate': 'mean',
                'performance_score': 'mean',
                'total_engagement': 'mean'
            }).reset_index()
            
            # Sort by engagement metrics
            best_hours = hourly_engagement.nlargest(5, 'engagement_rate')
            
            return [
                {
                    "hour": int(row['hour']),
                    "avg_engagement_rate": float(row['engagement_rate']),
                    "avg_performance_score": float(row['performance_score']),
                    "avg_total_engagement": float(row['total_engagement'])
                }
                for _, row in best_hours.iterrows()
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get optimal posting times: {e}")
            raise
    
    def get_content_recommendations(self) -> Dict[str, Any]:
        """Generate content recommendations based on performance analysis"""
        try:
            metrics = self.monitoring_service.metrics_history
            
            if not metrics:
                return {
                    "top_topics": [],
                    "recommended_hashtags": [],
                    "content_types": []
                }
            
            # Convert to DataFrame
            df = pd.DataFrame([vars(m) for m in metrics])
            
            # Analyze text content
            topics, hashtags = self._extract_topics_and_hashtags(df)
            
            # Calculate performance by content type
            content_types = self._analyze_content_types(df)
            
            return {
                "top_topics": topics,
                "recommended_hashtags": hashtags,
                "content_types": content_types
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get content recommendations: {e}")
            raise
    
    def _get_recent_metrics(self, days: int) -> List[TweetMetrics]:
        """Get metrics for specified time period"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [
            m for m in self.monitoring_service.metrics_history
            if datetime.fromisoformat(m.created_at) > cutoff_date
        ]
    
    def _generate_empty_summary(self, days: int) -> AnalyticsSummary:
        """Generate empty analytics summary"""
        now = datetime.utcnow()
        return AnalyticsSummary(
            period_start=(now - timedelta(days=days)).isoformat(),
            period_end=now.isoformat(),
            total_tweets=0,
            total_engagement=0,
            avg_engagement_rate=0.0,
            engagement_trend='',
            top_performing_tweets=[],
            engagement_by_hour={},
            content_performance={}
        )
    
    def _analyze_content_performance(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze performance by content type"""
        try:
            # Extract hashtags and keywords
            df['hashtags'] = df['text'].str.findall(r'#(\w+)')
            df['keywords'] = df['text'].str.split().apply(
                lambda x: [w.lower() for w in x if w.isalnum() and len(w) > 3]
            )
            
            # Calculate performance by hashtag
            hashtag_performance = {}
            for idx, row in df.iterrows():
                for tag in row['hashtags']:
                    if tag not in hashtag_performance:
                        hashtag_performance[tag] = []
                    hashtag_performance[tag].append(row['performance_score'])
            
            # Average performance by hashtag
            return {
                tag: np.mean(scores)
                for tag, scores in hashtag_performance.items()
                if len(scores) >= 3  # Require minimum sample size
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze content performance: {e}")
            raise
    
    def _extract_topics_and_hashtags(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Extract top topics and hashtags from tweets"""
        try:
            # Extract hashtags
            all_hashtags = []
            for text in df['text']:
                tags = [tag.lower() for tag in text.split() if tag.startswith('#')]
                all_hashtags.extend(tags)
            
            # Count and sort hashtags
            hashtag_counts = pd.Series(all_hashtags).value_counts()
            top_hashtags = hashtag_counts.head(10).index.tolist()
            
            # Extract topics (non-hashtag words)
            all_words = []
            for text in df['text']:
                words = [
                    word.lower() for word in text.split()
                    if word.isalnum() and not word.startswith('#') and len(word) > 3
                ]
                all_words.extend(words)
            
            # Count and sort topics
            word_counts = pd.Series(all_words).value_counts()
            top_topics = word_counts.head(10).index.tolist()
            
            return top_topics, top_hashtags
            
        except Exception as e:
            self.logger.error(f"Failed to extract topics and hashtags: {e}")
            raise
    
    def _analyze_content_types(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze performance by content type"""
        try:
            # Define content type patterns
            content_patterns = {
                "question": r'\?',
                "link": r'https?://\S+',
                "hashtag": r'#\w+',
                "mention": r'@\w+',
                "media": r'(photo|video|image)'
            }
            
            # Analyze each content type
            content_stats = []
            for content_type, pattern in content_patterns.items():
                # Find tweets with this content type
                mask = df['text'].str.contains(pattern, case=False)
                if mask.any():
                    avg_engagement = df[mask]['engagement_rate'].mean()
                    avg_performance = df[mask]['performance_score'].mean()
                    
                    content_stats.append({
                        "type": content_type,
                        "avg_engagement_rate": float(avg_engagement),
                        "avg_performance_score": float(avg_performance),
                        "tweet_count": int(mask.sum())
                    })
            
            return sorted(
                content_stats,
                key=lambda x: x['avg_performance_score'],
                reverse=True
            )
            
        except Exception as e:
            self.logger.error(f"Failed to analyze content types: {e}")
            raise 