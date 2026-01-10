"""
Base classes for search engines.
"""

from typing import List, Dict, Any


# Common User-Agent string used across all search engines
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


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
