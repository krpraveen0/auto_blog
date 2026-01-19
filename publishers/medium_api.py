"""
Medium publisher using Medium API
Creates interactive blog posts with diagrams and comprehensive paper analysis
"""

import os
import requests
import json
from pathlib import Path
from typing import Dict, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MediumPublisher:
    """Publish articles to Medium via Integration Token API"""
    
    API_BASE = "https://api.medium.com/v1"
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.auto_publish = config.get('auto_publish', False)
        
        # Get credentials from environment
        self.integration_token = os.getenv('MEDIUM_INTEGRATION_TOKEN')
        self.author_id = os.getenv('MEDIUM_AUTHOR_ID')
        
        if not self.integration_token:
            logger.warning("MEDIUM_INTEGRATION_TOKEN not set, publishing will fail")
        
        # Get author ID if not provided
        if self.integration_token and not self.author_id:
            self.author_id = self._get_author_id()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Medium API requests"""
        return {
            "Authorization": f"Bearer {self.integration_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Charset": "utf-8"
        }
    
    def _get_author_id(self) -> Optional[str]:
        """
        Get the authenticated user's Medium ID
        
        Returns:
            Author ID string or None
        """
        try:
            response = requests.get(
                f"{self.API_BASE}/me",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                author_id = data.get('data', {}).get('id')
                if author_id:
                    logger.info(f"Retrieved Medium author ID: {author_id}")
                    return author_id
            else:
                logger.error(f"Failed to get author ID: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error getting author ID: {e}")
        
        return None
    
    def _convert_markdown_to_medium(self, content: str) -> str:
        """
        Convert markdown content to Medium-compatible format
        Medium supports a subset of Markdown and HTML
        
        Args:
            content: Markdown content
            
        Returns:
            Medium-compatible content
        """
        # Medium supports:
        # - Markdown formatting
        # - Embedded images
        # - Code blocks with syntax highlighting
        # - Mermaid diagrams (via code blocks)
        
        # For now, return as-is since Medium accepts Markdown
        # In future, could add preprocessing for better formatting
        return content
    
    def _extract_metadata(self, content: str) -> Dict[str, any]:
        """
        Extract metadata from markdown frontmatter
        
        Args:
            content: Markdown content with YAML frontmatter
            
        Returns:
            Dictionary with title, tags, etc.
        """
        metadata = {
            'title': 'Untitled',
            'tags': [],
            'canonicalUrl': None
        }
        
        # Parse YAML frontmatter
        if content.startswith('---'):
            try:
                # Split frontmatter from content
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1])
                    
                    if frontmatter:
                        metadata['title'] = frontmatter.get('title', metadata['title'])
                        metadata['tags'] = frontmatter.get('tags', metadata['tags'])
                        metadata['canonicalUrl'] = frontmatter.get('canonical_url')
                        
                        # Get content without frontmatter
                        metadata['_content'] = parts[2].strip()
                    else:
                        metadata['_content'] = content
                else:
                    metadata['_content'] = content
            except Exception as e:
                logger.warning(f"Failed to parse frontmatter: {e}")
                metadata['_content'] = content
        else:
            # Try to extract title from first # heading
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    metadata['title'] = line[2:].strip()
                    break
            metadata['_content'] = content
        
        return metadata
    
    def publish(self, draft_path: Path, publish_status: str = 'draft') -> Dict:
        """
        Publish an article to Medium
        
        Args:
            draft_path: Path to markdown draft file
            publish_status: 'public', 'draft', or 'unlisted'
            
        Returns:
            Dict with 'success', 'post_url', and 'error' keys
        """
        if not self.enabled:
            logger.info("Medium publishing is disabled")
            return {'success': False, 'error': 'Publishing is disabled'}
        
        if not self.integration_token:
            logger.error("Medium integration token not configured")
            return {'success': False, 'error': 'Integration token not configured'}
        
        if not self.author_id:
            logger.error("Medium author ID not available")
            return {'success': False, 'error': 'Author ID not available'}
        
        try:
            # Read draft content
            with open(draft_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata
            metadata = self._extract_metadata(content)
            article_content = metadata.get('_content', content)
            
            # Convert to Medium format
            medium_content = self._convert_markdown_to_medium(article_content)
            
            # Prepare post data
            post_data = {
                'title': metadata['title'],
                'contentFormat': 'markdown',
                'content': medium_content,
                'publishStatus': publish_status,
                'tags': metadata['tags'][:5] if metadata['tags'] else []  # Medium allows max 5 tags
            }
            
            # Add canonical URL if provided
            if metadata['canonicalUrl']:
                post_data['canonicalUrl'] = metadata['canonicalUrl']
            
            # Make API request
            logger.info(f"Publishing to Medium: {metadata['title']}")
            response = requests.post(
                f"{self.API_BASE}/users/{self.author_id}/posts",
                headers=self._get_headers(),
                json=post_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                post_data = data.get('data', {})
                post_url = post_data.get('url', '')
                post_id = post_data.get('id', '')
                
                logger.info(f"Successfully published to Medium: {post_url}")
                
                return {
                    'success': True,
                    'post_url': post_url,
                    'post_id': post_id,
                    'title': metadata['title']
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Failed to publish to Medium: {error_msg}")
                
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Exception while publishing to Medium: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_post_url(self, draft_path: Path) -> str:
        """
        Get the URL where the post would be published
        (placeholder for unpublished content)
        
        Args:
            draft_path: Path to draft file
            
        Returns:
            Placeholder URL or empty string
        """
        # Medium URLs are only available after publishing
        return ""
    
    def validate_credentials(self) -> bool:
        """
        Validate Medium credentials
        
        Returns:
            True if credentials are valid
        """
        if not self.integration_token:
            return False
        
        try:
            response = requests.get(
                f"{self.API_BASE}/me",
                headers=self._get_headers(),
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False
