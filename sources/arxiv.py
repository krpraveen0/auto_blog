"""
arXiv fetcher using RSS feeds
"""

import feedparser
from datetime import datetime
from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ArxivFetcher:
    """Fetch papers from arXiv RSS feeds"""
    
    BASE_URL = "https://rss.arxiv.org/rss"
    
    def __init__(self, config: Dict):
        self.config = config
        self.categories = config.get('categories', ['cs.AI'])
        self.max_results = config.get('max_results', 20)
    
    def fetch(self) -> List[Dict]:
        """
        Fetch papers from arXiv
        
        Returns:
            List of paper dictionaries
        """
        all_papers = []
        
        for category in self.categories:
            try:
                url = f"{self.BASE_URL}/{category}"
                logger.info(f"Fetching arXiv papers from {category}")
                
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:self.max_results]:
                    paper = {
                        'id': entry.id.split('/')[-1],
                        'title': entry.title,
                        'url': entry.link,
                        'summary': entry.get('summary', ''),
                        'authors': [author.name for author in entry.get('authors', [])],
                        'published': entry.get('published', ''),
                        'category': category,
                        'source': 'arxiv',
                        'source_priority': 'high',
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    all_papers.append(paper)
                
                logger.info(f"Fetched {len(feed.entries[:self.max_results])} papers from {category}")
                
            except Exception as e:
                logger.error(f"Failed to fetch from {category}: {e}")
        
        return all_papers
