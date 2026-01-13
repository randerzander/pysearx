"""
Yep search engine implementation for pysearx.

Yep is a search engine by Ahrefs.
This implementation queries the Yep API and parses JSON results.
"""

from typing import List, Dict, Any
import re
import requests
from ..base import SearchEngine, DEFAULT_USER_AGENT, DEFAULT_HEADERS


class YepEngine(SearchEngine):
    """Yep search engine implementation."""
    
    def __init__(self):
        self.name = 'Yep'
        self.base_url = 'https://api.yep.com/fs/2/search'
        self.timeout = 10
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        # Check if we're currently rate limited
        self._check_rate_limit()
        
        Search Yep for the given query.
        
        Args:
            query: The search query string
            **kwargs: Additional parameters (currently unused)
            
        Returns:
            List of result dictionaries with title, url, description (deprecated), and summary
        """
        # Check if we're currently rate limited
        self._check_rate_limit()
        
        results = []
        
        try:
            # Prepare the request
            params = {
                'client': 'web',
                'no_correct': 'false',
                'q': query,
                'safeSearch': 'off',
                'type': 'web',
            }
            
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = 'https://yep.com/'
            headers['Origin'] = 'https://yep.com'
            
            # Make the request
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                    proxies=get_proxy_dict(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Check if response has results
            if len(data) < 2 or 'results' not in data[1]:
                return results
            
            # Extract results
            for result in data[1]['results']:
                try:
                    # Only process Organic results
                    if result.get('type') != 'Organic':
                        continue
                    
                    url = result.get('url', '')
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    
                    # Clean HTML from snippet
                    if snippet:
                        # Simple HTML tag removal
                        snippet = re.sub(r'<[^>]+>', '', snippet)
                    
                    # Only add if we have at least title and URL
                    if title and url:
                        results.append({
                            'title': title,
                            'url': url,
                            'description': snippet,  # deprecated, use summary
                            'summary': snippet
                        })
                        
                except (AttributeError, KeyError, TypeError):
                    # Skip malformed results
                    continue
            
        except requests.RequestException as e:
            error_str = str(e)
            # Check for rate limit
            if self._is_rate_limit_error(error_str):
                self._handle_rate_limit()
            raise Exception(f"Failed to query Yep: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Yep results: {e}")
        
        return results
