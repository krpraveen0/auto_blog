"""
LinkedIn publisher using UGC API
"""

import os
import requests
from pathlib import Path
from typing import Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LinkedInPublisher:
    """Publish posts to LinkedIn via UGC API"""
    
    API_BASE = "https://api.linkedin.com/v2"
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.auto_publish = config.get('auto_publish', False)
        
        # Get credentials from environment
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.user_id = os.getenv('LINKEDIN_USER_ID')
        
        if not self.access_token:
            logger.warning("LINKEDIN_ACCESS_TOKEN not set, publishing will fail")
        
        if not self.user_id:
            logger.warning("LINKEDIN_USER_ID not set, publishing will fail")
    
    def publish(self, draft_path: Path) -> bool:
        """
        Publish a LinkedIn draft
        
        Args:
            draft_path: Path to text draft file
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.info("LinkedIn publishing is disabled")
            return False
        
        if not self.access_token or not self.user_id:
            logger.error("LinkedIn credentials not configured")
            return False
        
        try:
            # Read draft content
            with open(draft_path, 'r') as f:
                content = f.read()
            
            # Publish via UGC API
            success = self._post_to_linkedin(content)
            
            if success:
                logger.info(f"Published LinkedIn post from {draft_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to publish to LinkedIn: {e}")
            return False
    
    def _post_to_linkedin(self, content: str) -> bool:
        """Post content to LinkedIn UGC API"""
        
        url = f"{self.API_BASE}/ugcPosts"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Build UGC post payload
        payload = {
            "author": f"urn:li:person:{self.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info("Successfully posted to LinkedIn")
            return True
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"LinkedIn API error: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Failed to post to LinkedIn: {e}")
            return False
    
    def get_profile(self) -> Dict:
        """Get LinkedIn profile information (for testing)"""
        if not self.access_token:
            return {}
        
        url = f"{self.API_BASE}/me"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get LinkedIn profile: {e}")
            return {}
