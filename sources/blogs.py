"""
Blog fetcher for company AI blogs using RSS
Optimized to randomly select ONE feed to reduce API requests
"""

import feedparser
import random
from datetime import datetime
from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BlogFetcher:
    """Fetch posts from AI company blogs via RSS - randomly selects one feed per run"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.feeds = config.get('feeds', [])
    
    def fetch(self) -> List[Dict]:
        """
        Fetch blog posts from ONE randomly selected RSS feed
        This optimizes API requests by not fetching from all feeds
        
        Returns:
            List of blog post dictionaries
        """
        if not self.feeds:
            logger.warning("No blog feeds configured")
            return []
        
        # Autonomous decision: randomly select one feed to save requests
        selected_feed = random.choice(self.feeds)
        
        logger.info(f"🎲 Randomly selected feed: {selected_feed['name']} (out of {len(self.feeds)} configured feeds)")
        logger.info(f"   This reduces API requests and improves efficiency")
        
        all_posts = []
        
        try:
            name = selected_feed['name']
            url = selected_feed['url']
            priority = selected_feed.get('priority', 'medium')
            
            logger.info(f"Fetching from {name} blog at {url}")
            
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
            
            logger.info(f"✅ Fetched {len(feed.entries)} posts from {name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch from {selected_feed.get('name', 'unknown')}: {e}")
            logger.info("💡 Tip: Check if the RSS feed URL is accessible and valid")
        
        return all_posts
