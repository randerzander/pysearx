"""
DuckDuckGo API-based search engine implementation for pysearx.

This implementation uses the 'ddgs' package which provides access to
DuckDuckGo's API endpoints without CAPTCHA or bot blocking issues.

The ddgs package is recommended over HTML scraping as it:
- Has no CAPTCHA challenges
- Has no bot detection/blocking
- Provides structured JSON data
- Is more reliable and easier to maintain

Installation: pip install ddgs
"""

from typing import List, Dict, Any
from ..base import SearchEngine

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False


class DuckDuckGoAPIEngine(SearchEngine):
    """
    DuckDuckGo search engine using the ddgs package.
    
    This engine uses the ddgs package which accesses DuckDuckGo's API
    endpoints directly, avoiding CAPTCHA and bot blocking issues that
    can occur with HTML scraping.
    
    Requires: pip install ddgs
    """
    
    def __init__(self):
        """Initialize the DuckDuckGo API engine."""
        if not DDGS_AVAILABLE:
            raise ImportError(
                "The 'ddgs' package is required for DuckDuckGoAPIEngine. "
                "Install it with: pip install ddgs"
            )
        self.name = 'DuckDuckGo-API'
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo using the ddgs package.
        
        Args:
            query: The search query string
            **kwargs: Additional parameters (currently unused)
            
        Returns:
            List of result dictionaries with title, url, and description
        """
        results = []
        
        try:
            # Create DDGS instance and perform search
            # Using context manager for proper resource cleanup
            with DDGS() as ddgs:
                # Get up to 20 results (we'll deduplicate and limit later)
                search_results = ddgs.text(query, max_results=20)
                
                # Convert ddgs results to our standard format
                for result in search_results:
                    # ddgs package returns: {title, href, body}
                    # We map to our standard format: {title, url, description}
                    if result.get('href') and result.get('title'):
                        results.append({
                            'title': result.get('title', ''),
                            'url': result.get('href', ''),  # href -> url
                            'description': result.get('body', '')  # body -> description
                        })
                        
        except Exception as e:
            # Log error and re-raise
            raise Exception(f"Failed to query DuckDuckGo API: {e}")
        
        return results


# Helper function to check if API engine is available
def is_available() -> bool:
    """
    Check if the DuckDuckGo API engine is available.
    
    Returns:
        True if ddgs package is installed, False otherwise
    """
    return DDGS_AVAILABLE
