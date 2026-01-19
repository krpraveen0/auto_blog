"""
GitHub Trending fetcher for ML/AI repositories
Enhanced to fetch comprehensive repository statistics and trending metrics
"""

import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from utils.logger import setup_logger
import os

logger = setup_logger(__name__)


class GitHubFetcher:
    """Fetch trending ML/AI repositories from GitHub with comprehensive statistics"""
    
    SEARCH_API = "https://api.github.com/search/repositories"
    REPO_API = "https://api.github.com/repos"
    
    def __init__(self, config: Dict):
        self.config = config
        self.topics = config.get('topics', ['machine-learning', 'artificial-intelligence'])
        self.min_stars = config.get('min_stars', 100)
        self.max_results = config.get('max_results', 10)
        
        # Use GitHub token if available for higher rate limits
        self.token = os.getenv('GH_PAGES_TOKEN') or os.getenv('GITHUB_TOKEN')
        self.headers = {}
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
    
    def fetch_repo_details(self, owner: str, repo: str) -> Optional[Dict]:
        """
        Fetch detailed repository information including languages, contributors, etc.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary with detailed repository stats or None if failed
        """
        try:
            # Fetch repository details
            repo_url = f"{self.REPO_API}/{owner}/{repo}"
            repo_response = requests.get(repo_url, headers=self.headers, timeout=10)
            repo_response.raise_for_status()
            repo_data = repo_response.json()
            
            # Fetch languages
            languages_url = f"{self.REPO_API}/{owner}/{repo}/languages"
            languages_response = requests.get(languages_url, headers=self.headers, timeout=10)
            languages = languages_response.json() if languages_response.status_code == 200 else {}
            
            # Fetch contributors count (only first page to avoid rate limits)
            contributors_url = f"{self.REPO_API}/{owner}/{repo}/contributors"
            contributors_response = requests.get(
                contributors_url, 
                headers=self.headers, 
                params={'per_page': 1, 'anon': 'true'},
                timeout=10
            )
            contributors_count = 0
            if contributors_response.status_code == 200:
                contributors_data = contributors_response.json()
                # Try to get count from Link header if available
                link_header = contributors_response.headers.get('Link', '')
                if 'last' in link_header:
                    try:
                        # Parse the last page number from Link header
                        match = re.search(r'page=(\d+)>; rel="last"', link_header)
                        if match:
                            contributors_count = int(match.group(1))
                    except Exception:
                        contributors_count = len(contributors_data)
                else:
                    contributors_count = len(contributors_data) if contributors_data else 0
            
            return {
                'watchers': repo_data.get('watchers_count', 0),
                'open_issues': repo_data.get('open_issues_count', 0),
                'license': repo_data.get('license', {}).get('name', '') if repo_data.get('license') else '',
                'default_branch': repo_data.get('default_branch', 'main'),
                'has_wiki': repo_data.get('has_wiki', False),
                'has_pages': repo_data.get('has_pages', False),
                'has_discussions': repo_data.get('has_discussions', False),
                'languages': languages,
                'contributors_count': contributors_count,
                'network_count': repo_data.get('network_count', 0),
                'subscribers_count': repo_data.get('subscribers_count', 0),
            }
            
        except Exception as e:
            logger.warning(f"Failed to fetch detailed stats for {owner}/{repo}: {e}")
            return None
    
    def calculate_trending_metrics(self, repo: Dict) -> Dict:
        """
        Calculate trending metrics for a repository
        
        Args:
            repo: Repository data
            
        Returns:
            Dictionary with trending metrics
        """
        created_at = datetime.fromisoformat(repo['created_at'].replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
        now = datetime.now(created_at.tzinfo)
        
        # Calculate days since creation
        days_since_creation = (now - created_at).days or 1  # Avoid division by zero
        
        # Calculate stars per day (velocity)
        stars_per_day = repo['stargazers_count'] / days_since_creation
        
        # Calculate forks per day
        forks_per_day = repo['forks_count'] / days_since_creation
        
        # Calculate days since last update
        days_since_update = (now - updated_at).days
        
        # Calculate activity score (recent activity is valued)
        activity_score = stars_per_day * 10 + forks_per_day * 5
        if days_since_update < 7:
            activity_score *= 2  # Boost for recently active repos
        
        return {
            'days_since_creation': days_since_creation,
            'days_since_update': days_since_update,
            'stars_per_day': round(stars_per_day, 2),
            'forks_per_day': round(forks_per_day, 2),
            'activity_score': round(activity_score, 2),
            'is_recently_active': days_since_update < 7
        }
    
    def fetch(self) -> List[Dict]:
        """
        Fetch trending AI/ML repositories from GitHub with comprehensive statistics
        
        Returns:
            List of repository dictionaries with detailed stats
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
                
                response = requests.get(self.SEARCH_API, params=params, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                for repo in data.get('items', []):
                    # Basic repository data
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
                        'owner_type': repo['owner']['type'],
                        'source': 'github',
                        'source_priority': 'medium',
                        'engagement_score': repo['stargazers_count'],
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    # Fetch detailed statistics
                    owner = repo['owner']['login']
                    repo_name = repo['name']
                    detailed_stats = self.fetch_repo_details(owner, repo_name)
                    
                    if detailed_stats:
                        repo_data.update(detailed_stats)
                    
                    # Calculate trending metrics
                    trending_metrics = self.calculate_trending_metrics(repo)
                    repo_data.update(trending_metrics)
                    
                    all_repos.append(repo_data)
                
                logger.info(f"Fetched {len(data.get('items', []))} repos with detailed stats for topic: {topic}")
                
            except Exception as e:
                logger.error(f"Failed to fetch GitHub repos for {topic}: {e}")
        
        # Remove duplicates by URL
        unique_repos = []
        seen_urls = set()
        for repo in all_repos:
            if repo['url'] not in seen_urls:
                unique_repos.append(repo)
                seen_urls.add(repo['url'])
        
        logger.info(f"Total unique repositories fetched: {len(unique_repos)}")
        return unique_repos
