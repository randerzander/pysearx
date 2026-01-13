"""
Mojeek search engine implementation for pysearx.

This is a simplified implementation that queries Mojeek
and parses the results.
"""

from typing import List, Dict, Any
import requests
from lxml import html
from ..base import SearchEngine, RateLimitMixin, DEFAULT_USER_AGENT, DEFAULT_HEADERS


class MojeekEngine(RateLimitMixin, SearchEngine):
    """Mojeek search engine implementation."""
    
    def __init__(self):
        RateLimitMixin.__init__(self)
        self.name = 'Mojeek'
        self.base_url = 'https://www.mojeek.com/search'
        self.timeout = 10
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Mojeek for the given query.
        
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
                'q': query,
                'safe': '0',  # safesearch off
                'lb': 'en',   # language: English
                'arc': 'all', # region: all
            }
            
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = 'https://www.mojeek.com/'
            
            # Make the request
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse HTML response
            tree = html.fromstring(response.content)
            
            # Find result elements
            result_elements = tree.xpath('//ul[@class="results-standard"]/li/a[@class="ob"]')
            
            for elem in result_elements:
                try:
                    # Extract URL
                    url = elem.get('href', '')
                    if not url:
                        continue
                    
                    # Extract title
                    title_elem = elem.xpath('../h2/a')
                    if not title_elem:
                        continue
                    title = title_elem[0].text_content().strip()
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('../p[@class="s"]')
                    description = ''
                    if snippet_elem:
                        description = snippet_elem[0].text_content().strip()
                    
                    # Only add if we have at least title and URL
                    if title and url:
                        results.append({
                            'title': title,
                            'url': url,
                            'description': description,  # deprecated, use summary
                            'summary': description
                        })
                        
                except (AttributeError, IndexError, KeyError, TypeError):
                    # Skip malformed results
                    continue
            
        except requests.RequestException as e:
            error_str = str(e)
            # Check for rate limit
            if self._is_rate_limit_error(error_str):
                self._handle_rate_limit()
            raise Exception(f"Failed to query Mojeek: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Mojeek results: {e}")
        
        # Request succeeded, reset rate limit state
        self._reset_rate_limit()
        return results
