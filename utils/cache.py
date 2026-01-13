"""
Simple caching utility
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional


class Cache:
    """Simple file-based cache with TTL"""
    
    def __init__(self, cache_dir: str = "data/cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache file name from key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        cache_file = self.cache_dir / f"{self._get_cache_key(key)}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                cache_file.unlink()  # Remove expired cache
                return None
            
            return data['value']
            
        except (json.JSONDecodeError, KeyError):
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Cache a value"""
        cache_file = self.cache_dir / f"{self._get_cache_key(key)}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'key': key,
            'value': value
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, default=str)
    
    def clear(self) -> None:
        """Clear all cache files"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
