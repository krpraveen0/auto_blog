"""
arXiv fetcher using official arxiv Python library
"""

import arxiv
from datetime import datetime, timedelta
from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ArxivFetcher:
    """Fetch papers from arXiv using official API"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.categories = config.get('categories', ['cs.AI'])
        self.max_results = config.get('max_results', 20)
        self.max_age_days = config.get('max_age_days', 7)
        
        # Initialize arxiv client with reasonable defaults
        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=3.0,  # Respect arXiv rate limits
            num_retries=3
        )
    
    def fetch(self) -> List[Dict]:
        """
        Fetch papers from arXiv
        
        Returns:
            List of paper dictionaries
        """
        all_papers = []
        
        # Calculate date range for recent papers
        date_from = datetime.now() - timedelta(days=self.max_age_days)
        
        for category in self.categories:
            try:
                logger.info(f"Fetching arXiv papers from category {category}")
                
                # Build query for recent papers in this category
                # Using simple category query - can be enhanced with arxivql for complex queries
                search = arxiv.Search(
                    query=f"cat:{category}",
                    max_results=self.max_results,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
                
                # Fetch results
                results = self.client.results(search)
                
                count = 0
                for result in results:
                    # Filter by date
                    if result.published.replace(tzinfo=None) < date_from:
                        continue
                    
                    paper = {
                        'id': result.get_short_id(),
                        'title': result.title,
                        'url': result.entry_id,
                        'pdf_url': result.pdf_url,
                        'summary': result.summary,
                        'authors': [author.name for author in result.authors],
                        'published': result.published.isoformat(),
                        'updated': result.updated.isoformat() if result.updated else None,
                        'category': category,
                        'categories': result.categories,  # All categories
                        'primary_category': result.primary_category,
                        'source': 'arxiv',
                        'source_priority': 'high',
                        'fetched_at': datetime.now().isoformat(),
                        'comment': result.comment,
                        'journal_ref': result.journal_ref,
                        'doi': result.doi
                    }
                    
                    all_papers.append(paper)
                    count += 1
                
                logger.info(f"Fetched {count} papers from {category}")
                
            except Exception as e:
                logger.error(f"Failed to fetch from {category}: {e}")
                # Continue with other categories even if one fails
                continue
        
        logger.info(f"Total papers fetched: {len(all_papers)}")
        return all_papers
