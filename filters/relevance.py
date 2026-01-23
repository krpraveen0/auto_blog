"""
Relevance filter using keywords and heuristics
"""

from datetime import datetime, timedelta
from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RelevanceFilter:
    """Filter content based on relevance criteria"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_age_days = config.get('max_age_days', 7)
        self.high_priority_keywords = [kw.lower() for kw in config.get('keywords', {}).get('high_priority', [])]
        self.medium_priority_keywords = [kw.lower() for kw in config.get('keywords', {}).get('medium_priority', [])]
        self.exclude_keywords = [kw.lower() for kw in config.get('exclude_keywords', [])]
        self.min_engagement_threshold = config.get('min_engagement_threshold', 100)
    
    def filter(self, items: List[Dict]) -> List[Dict]:
        """
        Filter items based on relevance criteria
        
        Args:
            items: List of content items
            
        Returns:
            Filtered list of relevant items
        """
        filtered = []
        
        for item in items:
            # Check age
            if not self._is_recent(item):
                continue
            
            # Check for excluded keywords
            if self._has_excluded_keywords(item):
                continue
            
            # Check for relevant keywords
            if not self._has_relevant_keywords(item):
                continue
            
            # Add keyword match score
            item['keyword_score'] = self._calculate_keyword_score(item)
            
            filtered.append(item)
        
        logger.info(f"Filtered {len(items)} items to {len(filtered)} relevant items")
        return filtered
    
    def _is_recent(self, item: Dict) -> bool:
        """Check if item is within max age"""
        try:
            published = item.get('published', '')
            if not published:
                # If no published date, assume it's recent (from fetch time)
                return True
            
            # Parse various date formats
            for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ', 
                       '%a, %d %b %Y %H:%M:%S %Z', '%Y-%m-%d']:
                try:
                    pub_date = datetime.strptime(published.replace('GMT', '+0000'), fmt)
                    if pub_date.tzinfo is None:
                        pub_date = pub_date.replace(tzinfo=None)
                    else:
                        pub_date = pub_date.replace(tzinfo=None)
                    
                    age = datetime.now() - pub_date
                    return age.days <= self.max_age_days
                except ValueError:
                    continue
            
            # If can't parse, assume recent
            return True
            
        except Exception as e:
            logger.debug(f"Error checking recency: {e}")
            return True
    
    def _has_excluded_keywords(self, item: Dict) -> bool:
        """Check if item contains excluded keywords"""
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        
        for keyword in self.exclude_keywords:
            if keyword in text:
                logger.debug(f"Excluded: {item.get('title', '')} (matched: {keyword})")
                return True
        
        return False
    
    def _has_relevant_keywords(self, item: Dict) -> bool:
        """Check if item contains relevant keywords"""
        if not self.high_priority_keywords and not self.medium_priority_keywords:
            # No keywords configured, accept all
            return True
        
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        
        # Check high priority keywords
        for keyword in self.high_priority_keywords:
            if keyword in text:
                return True
        
        # Check medium priority keywords
        for keyword in self.medium_priority_keywords:
            if keyword in text:
                return True
        
        # Accept high-engagement items even without keyword match
        # This helps with HackerNews stories that have high points but limited text
        engagement_keys = ['engagement_score', 'points', 'stars']
        engagement_score = next((item.get(key, 0) for key in engagement_keys if item.get(key, 0) > 0), 0)
        
        if engagement_score >= self.min_engagement_threshold:
            logger.debug(f"Accepted high-engagement item: {item.get('title', '')} (score: {engagement_score})")
            return True
        
        return False
    
    def _calculate_keyword_score(self, item: Dict) -> float:
        """Calculate keyword relevance score"""
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        
        score = 0.0
        
        # High priority keywords
        for keyword in self.high_priority_keywords:
            if keyword in text:
                score += 2.0
        
        # Medium priority keywords
        for keyword in self.medium_priority_keywords:
            if keyword in text:
                score += 1.0
        
        return score
