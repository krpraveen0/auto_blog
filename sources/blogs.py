"""
Blog fetcher for company AI blogs using RSS
"""

import feedparser
from datetime import datetime
from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BlogFetcher:
    """Fetch posts from AI company blogs via RSS"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.feeds = config.get('feeds', [])
    
    def fetch(self) -> List[Dict]:
        """
        Fetch blog posts from configured RSS feeds
        
        Returns:
            List of blog post dictionaries
        """
        all_posts = []
        
        for feed_config in self.feeds:
            try:
                name = feed_config['name']
                url = feed_config['url']
                priority = feed_config.get('priority', 'medium')
                
                logger.info(f"Fetching from {name} blog")
                
                feed = feedparser.parse(url)
                
                for entry in feed.entries:
                    post = {
                        'id': f"{name.lower().replace(' ', '_')}_{entry.id if hasattr(entry, 'id') else entry.link}",
                        'title': entry.title,
                        'url': entry.link,
                        'summary': entry.get('summary', entry.get('description', '')),
                        'published': entry.get('published', ''),
                        'author': entry.get('author', name),
                        'source': f"blog_{name.lower().replace(' ', '_')}",
                        'source_name': name,
                        'source_priority': priority,
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    all_posts.append(post)
                
                logger.info(f"Fetched {len(feed.entries)} posts from {name}")
                
            except Exception as e:
                logger.error(f"Failed to fetch from {feed_config.get('name', 'unknown')}: {e}")
        
        return all_posts
