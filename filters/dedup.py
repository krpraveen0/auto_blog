"""
Deduplication module using title similarity and URL hashing
"""

import hashlib
from typing import List, Dict
from difflib import SequenceMatcher
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Deduplicator:
    """Remove duplicate content items"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.similarity_threshold = config.get('title_similarity_threshold', 0.85)
        self.use_url_hash = config.get('url_hash', True)
    
    def deduplicate(self, items: List[Dict]) -> List[Dict]:
        """
        Remove duplicates from content items
        
        Args:
            items: List of content items
            
        Returns:
            Deduplicated list
        """
        if not items:
            return []
        
        unique_items = []
        seen_urls = set()
        seen_titles = []
        
        for item in items:
            # Check URL hash
            if self.use_url_hash:
                url_hash = self._hash_url(item.get('url', ''))
                if url_hash in seen_urls:
                    logger.debug(f"Duplicate URL: {item.get('title', '')}")
                    continue
                seen_urls.add(url_hash)
            
            # Check title similarity
            title = item.get('title', '').lower().strip()
            if self._is_similar_to_existing(title, seen_titles):
                logger.debug(f"Similar title: {item.get('title', '')}")
                continue
            
            seen_titles.append(title)
            unique_items.append(item)
        
        logger.info(f"Deduplicated {len(items)} items to {len(unique_items)} unique items")
        return unique_items
    
    def _hash_url(self, url: str) -> str:
        """Generate hash from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _is_similar_to_existing(self, title: str, existing_titles: List[str]) -> bool:
        """Check if title is similar to any existing title"""
        for existing in existing_titles:
            similarity = self._calculate_similarity(title, existing)
            if similarity >= self.similarity_threshold:
                return True
        return False
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings"""
        return SequenceMatcher(None, str1, str2).ratio()
