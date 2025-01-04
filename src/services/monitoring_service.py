from typing import Dict, List, Any, Optional
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class TweetMetrics:
    """Data class for tweet metrics"""
    tweet_id: str
    text: str
    created_at: str
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    quotes: int = 0
    total_engagement: int = 0
    engagement_rate: float = 0.0
    performance_score: float = 0.0

@dataclass
class PerformanceAlert:
    """Data class for performance alerts"""
    tweet_id: str
    alert_type: str
    message: str
    created_at: str
    metrics: Dict[str, Any]

class MonitoringService:
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize monitoring service"""
        self.logger = logging.getLogger(__name__)
        self.storage_dir = Path(storage_dir) if storage_dir else Path("monitoring")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage
        self.metrics_history: List[TweetMetrics] = []
        self.alerts: List[PerformanceAlert] = []
        self.performance_thresholds = {
            "high_engagement": 100,
            "low_engagement": 10,
            "viral_potential": 50
        }
        
        # Load existing data
        self._load_metrics_history()
    
    def track_tweet_metrics(self, tweet_data: Dict[str, Any], metrics: Dict[str, Any], follower_count: int) -> TweetMetrics:
        """Track metrics for a tweet and analyze performance"""
        try:
            # Calculate engagement rate (total engagement / follower count)
            total_engagement = sum(metrics.values())
            engagement_rate = (total_engagement / follower_count * 100) if follower_count > 0 else 0
            
            # Calculate performance score (weighted metric)
            weights = {"likes": 1.0, "retweets": 2.0, "replies": 1.5, "quotes": 1.5}
            performance_score = sum(
                metrics.get(k, 0) * weights[k]
                for k in weights.keys()
            ) / follower_count * 100 if follower_count > 0 else 0
            
            # Create metrics object
            tweet_metrics = TweetMetrics(
                tweet_id=tweet_data["id"],
                text=tweet_data["text"],
                created_at=tweet_data["created_at"],
                likes=metrics.get("likes", 0),
                retweets=metrics.get("retweets", 0),
                replies=metrics.get("replies", 0),
                quotes=metrics.get("quotes", 0),
                total_engagement=total_engagement,
                engagement_rate=engagement_rate,
                performance_score=performance_score
            )
            
            # Add to history
            self.metrics_history.append(tweet_metrics)
            
            # Check for alerts
            self._check_performance_alerts(tweet_metrics)
            
            # Save updated data
            self._save_metrics_history()
            
            self.logger.info(f"Tracked metrics for tweet {tweet_data['id']}")
            return tweet_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to track tweet metrics: {e}")
            raise
    
    def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get performance trends over specified time period"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Filter recent metrics
            recent_metrics = [
                m for m in self.metrics_history
                if datetime.fromisoformat(m.created_at) > cutoff_date
            ]
            
            if not recent_metrics:
                return {
                    "average_engagement": 0,
                    "engagement_trend": "stable",
                    "top_tweets": [],
                    "performance_summary": "No recent data"
                }
            
            # Calculate trends
            engagement_rates = [m.engagement_rate for m in recent_metrics]
            avg_engagement = sum(engagement_rates) / len(engagement_rates)
            
            # Sort by performance score
            top_tweets = sorted(
                recent_metrics,
                key=lambda x: x.performance_score,
                reverse=True
            )[:5]
            
            # Determine trend
            if len(engagement_rates) > 1:
                trend = "increasing" if engagement_rates[-1] > engagement_rates[0] else "decreasing"
            else:
                trend = "stable"
            
            return {
                "average_engagement": avg_engagement,
                "engagement_trend": trend,
                "top_tweets": [asdict(t) for t in top_tweets],
                "performance_summary": self._generate_performance_summary(recent_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance trends: {e}")
            raise
    
    def get_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""
        try:
            return [asdict(alert) for alert in self.alerts[-count:]]
        except Exception as e:
            self.logger.error(f"Failed to get alerts: {e}")
            raise
    
    def _check_performance_alerts(self, metrics: TweetMetrics) -> None:
        """Check for performance alerts based on metrics"""
        try:
            alerts = []
            
            # Check high engagement
            if metrics.engagement_rate > self.performance_thresholds["high_engagement"]:
                alerts.append(PerformanceAlert(
                    tweet_id=metrics.tweet_id,
                    alert_type="high_engagement",
                    message=f"Tweet has high engagement rate: {metrics.engagement_rate:.1f}%",
                    created_at=datetime.utcnow().isoformat(),
                    metrics=asdict(metrics)
                ))
            
            # Check low engagement
            elif metrics.engagement_rate < self.performance_thresholds["low_engagement"]:
                alerts.append(PerformanceAlert(
                    tweet_id=metrics.tweet_id,
                    alert_type="low_engagement",
                    message=f"Tweet has low engagement rate: {metrics.engagement_rate:.1f}%",
                    created_at=datetime.utcnow().isoformat(),
                    metrics=asdict(metrics)
                ))
            
            # Check viral potential
            if metrics.performance_score > self.performance_thresholds["viral_potential"]:
                alerts.append(PerformanceAlert(
                    tweet_id=metrics.tweet_id,
                    alert_type="viral_potential",
                    message=f"Tweet shows viral potential with score: {metrics.performance_score:.1f}",
                    created_at=datetime.utcnow().isoformat(),
                    metrics=asdict(metrics)
                ))
            
            # Add new alerts
            self.alerts.extend(alerts)
            
            # Save alerts
            self._save_alerts()
            
        except Exception as e:
            self.logger.error(f"Failed to check performance alerts: {e}")
            raise
    
    def _generate_performance_summary(self, metrics: List[TweetMetrics]) -> str:
        """Generate a summary of performance metrics"""
        try:
            avg_engagement = sum(m.engagement_rate for m in metrics) / len(metrics)
            avg_performance = sum(m.performance_score for m in metrics) / len(metrics)
            
            if avg_performance > self.performance_thresholds["high_engagement"]:
                status = "excellent"
            elif avg_performance > self.performance_thresholds["viral_potential"]:
                status = "good"
            elif avg_performance > self.performance_thresholds["low_engagement"]:
                status = "average"
            else:
                status = "needs improvement"
            
            return (
                f"Performance is {status} with average engagement rate of {avg_engagement:.1f}% "
                f"and average performance score of {avg_performance:.1f}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance summary: {e}")
            raise
    
    def _save_metrics_history(self) -> None:
        """Save metrics history to file"""
        try:
            metrics_file = self.storage_dir / "metrics_history.json"
            data = [asdict(m) for m in self.metrics_history]
            
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save metrics history: {e}")
            raise
    
    def _save_alerts(self) -> None:
        """Save alerts to file"""
        try:
            alerts_file = self.storage_dir / "alerts.json"
            data = [asdict(a) for a in self.alerts]
            
            with open(alerts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save alerts: {e}")
            raise
    
    def _load_metrics_history(self) -> None:
        """Load metrics history from file"""
        try:
            metrics_file = self.storage_dir / "metrics_history.json"
            alerts_file = self.storage_dir / "alerts.json"
            
            if metrics_file.exists():
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metrics_history = [TweetMetrics(**m) for m in data]
            
            if alerts_file.exists():
                with open(alerts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.alerts = [PerformanceAlert(**a) for a in data]
                    
        except Exception as e:
            self.logger.error(f"Failed to load metrics history: {e}")
            raise 