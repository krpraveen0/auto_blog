"""
Content ranker to score and prioritize items
"""

from typing import List, Dict
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentRanker:
    """Rank and score content items"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.weights = config.get('weights', {
            'recency': 0.3,
            'source_priority': 0.3,
            'keyword_match': 0.2,
            'engagement': 0.2
        })
    
    def rank(self, items: List[Dict]) -> List[Dict]:
        """
        Rank items by calculated score
        
        Args:
            items: List of content items
            
        Returns:
            Sorted list with scores
        """
        # Calculate scores
        for item in items:
            item['score'] = self._calculate_score(item)
        
        # Sort by score (descending)
        ranked = sorted(items, key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Ranked {len(ranked)} items")
        return ranked
    
    def _calculate_score(self, item: Dict) -> float:
        """Calculate overall score for an item"""
        recency_score = self._recency_score(item)
        priority_score = self._source_priority_score(item)
        keyword_score = self._keyword_score(item)
        engagement_score = self._engagement_score(item)
        
        total_score = (
            recency_score * self.weights['recency'] +
            priority_score * self.weights['source_priority'] +
            keyword_score * self.weights['keyword_match'] +
            engagement_score * self.weights['engagement']
        )
        
        return round(total_score, 2)
    
    def _recency_score(self, item: Dict) -> float:
        """Score based on recency (0-10)"""
        try:
            published = item.get('published', '')
            if not published:
                return 5.0  # Default mid-score if no date
            
            # Parse date
            for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ', 
                       '%a, %d %b %Y %H:%M:%S %Z', '%Y-%m-%d']:
                try:
                    pub_date = datetime.strptime(published.replace('GMT', '+0000'), fmt)
                    if pub_date.tzinfo:
                        pub_date = pub_date.replace(tzinfo=None)
                    
                    age_days = (datetime.now() - pub_date).days
                    
                    # Score: 10 for today, decreasing linearly
                    score = max(0, 10 - age_days)
                    return min(score, 10.0)
                    
                except ValueError:
                    continue
            
            return 5.0  # Default if can't parse
            
        except Exception:
            return 5.0
    
    def _source_priority_score(self, item: Dict) -> float:
        """Score based on source priority (0-10)"""
        priority = item.get('source_priority', 'medium').lower()
        
        priority_map = {
            'high': 10.0,
            'medium': 6.0,
            'low': 3.0
        }
        
        return priority_map.get(priority, 5.0)
    
    def _keyword_score(self, item: Dict) -> float:
        """Score based on keyword matches (0-10)"""
        raw_score = item.get('keyword_score', 0)
        
        # Normalize to 0-10 range (assuming max ~5 keywords)
        return min(raw_score * 2, 10.0)
    
    def _engagement_score(self, item: Dict) -> float:
        """Score based on engagement metrics (0-10)"""
        source = item.get('source', '')
        
        if source == 'hackernews':
            points = item.get('points', 0)
            # Normalize: 50-500+ points -> 0-10
            return min((points / 50), 10.0)
        
        elif source == 'github':
            stars = item.get('stars', 0)
            # Normalize: 100-1000+ stars -> 0-10
            return min((stars / 100), 10.0)
        
        elif source == 'arxiv':
            # arXiv doesn't have direct engagement metrics
            # Use category as proxy (cs.AI is more popular)
            category = item.get('category', '')
            if 'AI' in category:
                return 8.0
            return 6.0
        
        else:
            # Blog posts - default medium engagement
            return 5.0
