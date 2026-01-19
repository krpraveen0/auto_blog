"""
GitHub Pages publisher - commits markdown files to gh-pages branch
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict
from github import Github
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GitHubPagesPublisher:
    """Publish blog posts to GitHub Pages"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.auto_publish = config.get('auto_publish', False)
        
        gh_config = config.get('github_pages', {})
        self.branch = gh_config.get('branch', 'gh-pages')
        self.path = gh_config.get('path', '_posts')
        
        # Initialize GitHub client
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            logger.warning("GITHUB_TOKEN not set, publishing will fail")
            self.github = None
        else:
            self.github = Github(github_token)
        
        # Get repo from env
        repo_name = os.getenv('GITHUB_REPO')
        if repo_name and self.github:
            self.repo = self.github.get_repo(repo_name)
            logger.info(f"Initialized GitHub publisher for {repo_name}")
        else:
            self.repo = None
            logger.warning("GITHUB_REPO not set")
    
    def publish(self, draft_path: Path) -> bool:
        """
        Publish a blog draft to GitHub Pages
        
        Args:
            draft_path: Path to markdown draft file
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.info("GitHub Pages publishing is disabled")
            return False
        
        if not self.repo:
            logger.error("GitHub repository not configured")
            return False
        
        try:
            # Read draft content
            with open(draft_path, 'r') as f:
                content = f.read()
            
            # Generate filename with date
            date_prefix = datetime.now().strftime('%Y-%m-%d')
            filename = f"{date_prefix}-{draft_path.stem}.md"
            file_path = f"{self.path}/{filename}"
            
            # Check if file already exists
            try:
                existing = self.repo.get_contents(file_path, ref=self.branch)
                # Update existing file
                self.repo.update_file(
                    file_path,
                    f"Update post: {filename}",
                    content,
                    existing.sha,
                    branch=self.branch
                )
                logger.info(f"Updated existing post: {file_path}")
            except:
                # Create new file
                self.repo.create_file(
                    file_path,
                    f"Add post: {filename}",
                    content,
                    branch=self.branch
                )
                logger.info(f"Created new post: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish to GitHub Pages: {e}")
            return False
    
    def get_post_url(self, draft_path: Path) -> str:
        """
        Get the public URL for a published post
        
        Args:
            draft_path: Path to the draft file
            
        Returns:
            Public URL to the post
        """
        if not self.repo:
            return ""
        
        # Generate expected filename
        date_prefix = datetime.now().strftime('%Y-%m-%d')
        filename = f"{date_prefix}-{draft_path.stem}.md"
        
        # Construct GitHub Pages URL
        # Format: https://username.github.io/repo-name/year/month/day/post-title.html
        repo_parts = self.repo.full_name.split('/')
        username = repo_parts[0]
        repo_name = repo_parts[1] if len(repo_parts) > 1 else ''
        
        # Extract date parts
        year = datetime.now().strftime('%Y')
        month = datetime.now().strftime('%m')
        day = datetime.now().strftime('%d')
        
        # Post slug (remove date prefix and extension)
        slug = draft_path.stem
        
        return f"https://{username}.github.io/{repo_name}/{year}/{month}/{day}/{slug}.html"
    
    def list_published(self) -> list:
        """List all published posts"""
        if not self.repo:
            return []
        
        try:
            contents = self.repo.get_contents(self.path, ref=self.branch)
            return [c.name for c in contents if c.name.endswith('.md')]
        except Exception as e:
            logger.error(f"Failed to list published posts: {e}")
            return []
