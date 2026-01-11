"""
Base classes for search engines.
"""

from typing import List, Dict, Any, Optional
import time
import os
import random


# Common User-Agent string used across all search engines
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# More realistic headers to avoid bot detection
# Note: Don't include Accept-Encoding as requests handles it automatically
DEFAULT_HEADERS = {
    'User-Agent': DEFAULT_USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}


class RateLimitMixin:
    """Mixin to add exponential backoff rate limit handling to search engines."""
    
    def __init__(self):
        self._rate_limited_until = 0  # Timestamp when rate limit expires
        self._rate_limit_count = 0    # Number of consecutive rate limits
        self._base_backoff = 1        # Base backoff in seconds (1s)
        self._max_backoff = 300       # Maximum backoff (5 minutes)
    
    def _check_rate_limit(self):
        """Check if engine is currently rate limited."""
        if self._rate_limited_until > 0:
            current_time = time.time()
            if current_time < self._rate_limited_until:
                wait_time = int(self._rate_limited_until - current_time)
                raise Exception(f"Rate limited. Try again in {wait_time} seconds.")
            else:
                # Rate limit expired, reset count
                self._rate_limited_until = 0
                self._rate_limit_count = 0
    
    def _handle_rate_limit(self):
        """Mark engine as rate limited with exponential backoff."""
        self._rate_limit_count += 1
        
        # Calculate exponential backoff: base * 2^(count-1)
        # Example: 1s, 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 300s (max)
        backoff_seconds = min(
            self._base_backoff * (2 ** (self._rate_limit_count - 1)),
            self._max_backoff
        )
        
        self._rate_limited_until = time.time() + backoff_seconds
        engine_name = getattr(self, 'name', self.__class__.__name__)
        print(f"[{engine_name}] Rate limited (429). Attempt #{self._rate_limit_count}, "
              f"backing off for {backoff_seconds}s (exponential backoff).")
    
    def _is_rate_limit_error(self, error_str: str) -> bool:
        """Check if error is a rate limit error or blocking."""
        return ('429' in error_str or 
                'rate limit' in error_str.lower() or 
                'too many requests' in error_str.lower() or
                '403' in error_str)  # 403 Forbidden also indicates blocking


class SearchEngine:
    """Base class for search engine implementations."""
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute a search query.
        
        Args:
            query: The search query string
            **kwargs: Additional engine-specific parameters
            
        Returns:
            List of result dictionaries, each containing:
                - title: Result title
                - url: Result URL
                - description: Result description/snippet
        """
        raise NotImplementedError("Subclasses must implement search()")


class ProxyManager:
    """Manages proxy rotation from a file."""
    
    _proxies: Optional[List[str]] = None
    _current_index: int = 0
    
    @classmethod
    def load_proxies(cls, proxy_file: str) -> List[str]:
        """Load proxies from file."""
        if cls._proxies is None:
            try:
                with open(proxy_file, 'r') as f:
                    cls._proxies = [line.strip() for line in f if line.strip()]
                print(f"[ProxyManager] Loaded {len(cls._proxies)} proxies from {proxy_file}")
            except FileNotFoundError:
                print(f"[ProxyManager] Warning: {proxy_file} not found")
                cls._proxies = []
        return cls._proxies
    
    @classmethod
    def get_next_proxy(cls) -> Optional[str]:
        """Get next proxy in rotation."""
        if not cls._proxies:
            return None
        
        proxy = cls._proxies[cls._current_index]
        cls._current_index = (cls._current_index + 1) % len(cls._proxies)
        return proxy
    
    @classmethod
    def get_random_proxy(cls) -> Optional[str]:
        """Get random proxy from pool."""
        if not cls._proxies:
            return None
        return random.choice(cls._proxies)


def get_proxy_dict(proxy_url: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    Get proxy dictionary for requests library.
    
    Checks PROXY_FILE environment variable if proxy_url not provided.
    
    Args:
        proxy_url: Optional proxy URL (e.g., '1.2.3.4:8080')
    
    Returns:
        Dict for requests proxies parameter, or None
    """
    # If explicit proxy provided, use it
    if proxy_url:
        return {
            'http': f'http://{proxy_url}',
            'https': f'http://{proxy_url}',
        }
    
    # Check environment variable
    proxy_file = os.getenv('PROXY_FILE')
    if not proxy_file:
        return None
    
    # Load proxies from file
    proxies = ProxyManager.load_proxies(proxy_file)
    if not proxies:
        return None
    
    # Get next proxy in rotation
    proxy_url = ProxyManager.get_next_proxy()
    if proxy_url:
        return {
            'http': f'http://{proxy_url}',
            'https': f'http://{proxy_url}',
        }
    
    return None
