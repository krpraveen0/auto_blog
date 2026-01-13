"""
GitHub Trending fetcher for ML/AI repositories
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GitHubFetcher:
    """Fetch trending ML/AI repositories from GitHub"""
    
    SEARCH_API = "https://api.github.com/search/repositories"
    
    def __init__(self, config: Dict):
        self.config = config
        self.topics = config.get('topics', ['machine-learning', 'artificial-intelligence'])
        self.min_stars = config.get('min_stars', 100)
        self.max_results = config.get('max_results', 10)
    
    def fetch(self) -> List[Dict]:
        """
        Fetch trending AI/ML repositories from GitHub
        
        Returns:
            List of repository dictionaries
        """
        all_repos = []
        
        # Search for repos created or updated in last 7 days
        since_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        for topic in self.topics:
            try:
                query = f"topic:{topic} created:>={since_date} stars:>={self.min_stars}"
                
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': self.max_results
                }
                
                logger.info(f"Fetching GitHub repos with topic: {topic}")
                
                response = requests.get(self.SEARCH_API, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                for repo in data.get('items', []):
                    repo_data = {
                        'id': f"github_{repo['id']}",
                        'title': repo['full_name'],
                        'url': repo['html_url'],
                        'summary': repo.get('description', ''),
                        'stars': repo['stargazers_count'],
                        'forks': repo['forks_count'],
                        'language': repo.get('language', ''),
                        'topics': repo.get('topics', []),
                        'published': repo.get('created_at', ''),
                        'updated': repo.get('updated_at', ''),
                        'author': repo['owner']['login'],
                        'source': 'github',
                        'source_priority': 'medium',
                        'engagement_score': repo['stargazers_count'],
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    all_repos.append(repo_data)
                
                logger.info(f"Fetched {len(data.get('items', []))} repos for topic: {topic}")
                
            except Exception as e:
                logger.error(f"Failed to fetch GitHub repos for {topic}: {e}")
        
        # Remove duplicates by URL
        unique_repos = []
        seen_urls = set()
        for repo in all_repos:
            if repo['url'] not in seen_urls:
                unique_repos.append(repo)
                seen_urls.add(repo['url'])
        
        return unique_repos
