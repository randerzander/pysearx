"""
Base classes for search engines.
"""

from typing import List, Dict, Any


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
