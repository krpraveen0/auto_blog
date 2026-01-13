"""
Hacker News fetcher for AI/ML tagged stories
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class HackerNewsFetcher:
    """Fetch AI/ML stories from Hacker News"""
    
    API_BASE = "https://hacker-news.firebaseio.com/v0"
    ALGOLIA_API = "https://hn.algolia.com/api/v1"
    
    def __init__(self, config: Dict):
        self.config = config
        self.filter_tags = config.get('filter_tags', ['ai', 'ml'])
        self.min_points = config.get('min_points', 50)
        self.max_results = config.get('max_results', 15)
    
    def fetch(self) -> List[Dict]:
        """
        Fetch AI/ML stories from Hacker News using Algolia search
        
        Returns:
            List of HN story dictionaries
        """
        all_stories = []
        
        try:
            # Use Algolia HN search for better filtering
            query_tags = ','.join(self.filter_tags)
            
            for tag in self.filter_tags:
                url = f"{self.ALGOLIA_API}/search"
                params = {
                    'query': tag,
                    'tags': 'story',
                    'numericFilters': f'points>={self.min_points}',
                    'hitsPerPage': self.max_results
                }
                
                logger.info(f"Fetching HN stories with tag: {tag}")
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                for hit in data.get('hits', []):
                    story = {
                        'id': f"hn_{hit['objectID']}",
                        'title': hit.get('title', ''),
                        'url': hit.get('url', f"https://news.ycombinator.com/item?id={hit['objectID']}"),
                        'summary': hit.get('story_text', '')[:500],  # First 500 chars
                        'author': hit.get('author', ''),
                        'points': hit.get('points', 0),
                        'num_comments': hit.get('num_comments', 0),
                        'published': hit.get('created_at', ''),
                        'source': 'hackernews',
                        'source_priority': 'medium',
                        'engagement_score': hit.get('points', 0),
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    all_stories.append(story)
                
                logger.info(f"Fetched {len(data.get('hits', []))} stories for tag: {tag}")
            
            # Remove duplicates by URL
            unique_stories = []
            seen_urls = set()
            for story in all_stories:
                if story['url'] not in seen_urls:
                    unique_stories.append(story)
                    seen_urls.add(story['url'])
            
            return unique_stories
            
        except Exception as e:
            logger.error(f"Failed to fetch from Hacker News: {e}")
            return []
