"""
LinkedIn publisher using REST API
"""

import os
import requests
import json
from pathlib import Path
from typing import Dict, Tuple
from utils.logger import setup_logger

logger = setup_logger(__name__)

# LinkedIn API constants
MAX_CONTENT_LENGTH = 3000  # LinkedIn's typical character limit for text posts


class LinkedInPublisher:
    """Publish posts to LinkedIn via REST API"""
    
    API_BASE = "https://api.linkedin.com"
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.auto_publish = config.get('auto_publish', False)
        
        # Get credentials from environment
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.user_id = os.getenv('LINKEDIN_USER_ID')
        self.user_urn = None
        
        if not self.access_token:
            logger.warning("LINKEDIN_ACCESS_TOKEN not set, publishing will fail")
        
        if not self.user_id:
            logger.warning("LINKEDIN_USER_ID not set, publishing will fail")
        else:
            # Ensure user_id is properly formatted as URN
            self.user_urn = self._normalize_user_urn(self.user_id)
    
    def _normalize_user_urn(self, user_id: str) -> str:
        """
        Normalize user ID to URN format.
        Handles both plain IDs and already-formatted URNs.
        
        Args:
            user_id: Either plain ID (e.g., 'aQxKAY9vaq') or URN (e.g., 'urn:li:person:aQxKAY9vaq')
            
        Returns:
            Properly formatted URN
        """
        if user_id.startswith('urn:li:person:'):
            return user_id
        return f"urn:li:person:{user_id}"
    
    def _validate_content(self, content: str) -> Tuple[bool, str]:
        """
        Validate post content before publishing.
        
        Args:
            content: Post content to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content or not content.strip():
            return False, "Content cannot be empty"
        
        if len(content) > MAX_CONTENT_LENGTH:
            return False, f"Content exceeds {MAX_CONTENT_LENGTH} character limit (got {len(content)})"
        
        return True, ""
    
    def publish(self, draft_path: Path) -> Dict:
        """
        Publish a LinkedIn draft
        
        Args:
            draft_path: Path to text draft file
            
        Returns:
            Dict with 'success', 'post_url', and 'error' keys
        """
        if not self.enabled:
            logger.info("LinkedIn publishing is disabled")
            return {'success': False, 'error': 'Publishing is disabled'}
        
        if not self.access_token or not self.user_id:
            logger.error("LinkedIn credentials not configured")
            return {'success': False, 'error': 'Credentials not configured'}
        
        try:
            # Read draft content
            with open(draft_path, 'r') as f:
                content = f.read()
            
            # Validate content before posting
            is_valid, error_msg = self._validate_content(content)
            if not is_valid:
                logger.error(f"Content validation failed: {error_msg}")
                return {'success': False, 'error': error_msg}
            
            # Publish via REST API
            result = self._post_to_linkedin(content)
            
            if result.get('success'):
                logger.info(f"Published LinkedIn post from {draft_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to publish to LinkedIn: {e}")
            return {'success': False, 'error': str(e)}
    
    def _post_to_linkedin(self, content: str) -> Dict:
        """Post content to LinkedIn v2 UGC API"""
        
        url = f"{self.API_BASE}/v2/ugcPosts"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Build v2 UGC API post payload
        payload = {
            "author": self.user_urn,
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
        
        # Log sanitized payload for debugging (without auth token)
        debug_payload = payload.copy()
        logger.debug(f"LinkedIn API request to {url} with payload: {json.dumps(debug_payload, indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Check for successful response (201 Created)
            if response.status_code == 201:
                logger.info("Successfully posted to LinkedIn (201 Created)")
                
                # Extract post ID from response headers or body
                post_id = None
                response_data = response.json() if response.content else {}
                
                # LinkedIn returns post ID in 'id' field or x-restli-id header
                if 'id' in response_data:
                    post_id = response_data['id']
                elif 'x-restli-id' in response.headers:
                    post_id = response.headers['x-restli-id']
                
                # Construct post URL using the returned URN type
                post_url = ''
                if post_id:
                    # Examples:
                    # urn:li:activity:123 -> https://www.linkedin.com/feed/update/urn:li:activity:123/
                    # urn:li:share:123    -> https://www.linkedin.com/feed/update/urn:li:share:123/
                    # activity:123         -> https://www.linkedin.com/feed/update/activity:123/
                    # share:123            -> https://www.linkedin.com/feed/update/share:123/
                    if post_id.startswith('urn:li:activity:') or post_id.startswith('urn:li:share:'):
                        post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
                    elif post_id.startswith('activity:') or post_id.startswith('share:'):
                        post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
                    else:
                        # Fallback: assume share URN when shape is unknown
                        post_url = f"https://www.linkedin.com/feed/update/urn:li:share:{post_id}/"
                
                return {'success': True, 'post_url': post_url, 'post_id': post_id}
            else:
                # LinkedIn REST API returns 201 for successful post creation
                # Any other status code (including other 2xx codes) means the post was not created
                error_msg = f"LinkedIn API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {'success': False, 'error': error_msg}
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error(f"LinkedIn API {error_msg}")
            return {'success': False, 'error': error_msg}
        except requests.exceptions.Timeout:
            error_msg = "Request timed out (30 seconds)"
            logger.error(f"LinkedIn API {error_msg}")
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to post to LinkedIn: {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def get_profile(self) -> Dict:
        """
        Get LinkedIn profile information (for testing)
        Note: Uses v2 API as userinfo endpoint hasn't migrated to REST API yet
        """
        if not self.access_token:
            return {}
        
        url = f"{self.API_BASE}/v2/userinfo"
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
