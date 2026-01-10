"""
Core search functionality for pysearx.

This module provides the main search() function and coordinates
search engine queries.
"""

from typing import List, Dict, Any, Optional
from .engines.duckduckgo import DuckDuckGoEngine


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


# Default engines to use
DEFAULT_ENGINES = [
    DuckDuckGoEngine(),
]


def search(query: str, engines: Optional[List[SearchEngine]] = None, 
           max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search for a query across multiple search engines.
    
    This is the main API function for pysearx. It queries the specified
    search engines and returns aggregated results.
    
    Args:
        query: The search query string
        engines: List of SearchEngine instances to use. If None, uses defaults.
        max_results: Maximum number of results to return (default: 10)
        
    Returns:
        List of result dictionaries, each containing:
            - title: Result title (str)
            - url: Result URL (str)
            - description: Result description/snippet (str)
            - engine: Name of the engine that returned this result (str)
            
    Example:
        >>> results = search("python programming")
        >>> for result in results:
        ...     print(f"{result['title']}: {result['url']}")
    """
    if engines is None:
        engines = DEFAULT_ENGINES
    
    all_results = []
    seen_urls = set()
    
    for engine in engines:
        try:
            engine_results = engine.search(query)
            
            # Add engine name and deduplicate by URL
            for result in engine_results:
                url = result.get('url', '')
                if url and url not in seen_urls:
                    result['engine'] = engine.__class__.__name__
                    all_results.append(result)
                    seen_urls.add(url)
                    
                    if len(all_results) >= max_results:
                        break
            
            if len(all_results) >= max_results:
                break
                
        except Exception as e:
            # Log error but continue with other engines
            print(f"Error searching with {engine.__class__.__name__}: {e}")
            continue
    
    return all_results[:max_results]
