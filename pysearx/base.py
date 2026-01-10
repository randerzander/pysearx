"""
Base classes for search engines.
"""

from typing import List, Dict, Any


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
