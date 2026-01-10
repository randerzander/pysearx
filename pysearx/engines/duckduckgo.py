"""
DuckDuckGo search engine implementation for pysearx.

This is a simplified implementation that queries DuckDuckGo HTML
and parses the results without requiring JavaScript.
"""

from typing import List, Dict, Any
import requests
from lxml import html
from ..base import SearchEngine, DEFAULT_USER_AGENT, DEFAULT_HEADERS

try:
    from ..browser import fetch_with_browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class DuckDuckGoEngine(SearchEngine):
    """DuckDuckGo search engine implementation."""
    
    def __init__(self):
        self.name = 'DuckDuckGo'
        self.base_url = 'https://html.duckduckgo.com/html/'
        self.timeout = 10
        self.use_browser = PLAYWRIGHT_AVAILABLE  # Use browser if available
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo for the given query.
        
        Args:
            query: The search query string
            **kwargs: Additional parameters (currently unused)
            
        Returns:
            List of result dictionaries with title, url, and description
        """
        results = []
        
        try:
            if self.use_browser and PLAYWRIGHT_AVAILABLE:
                # Use Playwright for better bot detection evasion
                from urllib.parse import urlencode
                params = {
                    'q': query,
                    'b': '',
                    'kl': 'wt-wt',
                }
                url = f"{self.base_url}?{urlencode(params)}"
                response_content = fetch_with_browser(url, timeout=self.timeout * 1000)
                tree = html.fromstring(response_content)
            else:
                # Fallback to requests
                params = {
                    'q': query,
                    'b': '',
                    'kl': 'wt-wt',
                }
                
                # Use realistic headers
                headers = DEFAULT_HEADERS.copy()
                headers['Referer'] = 'https://duckduckgo.com/'
                
                # Make the request
                response = requests.post(
                    self.base_url,
                    data=params,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                tree = html.fromstring(response.content)
            
            # Find result links
            # DuckDuckGo HTML structure uses result-link class for links
            result_elements = tree.xpath('//div[contains(@class, "result")]')
            
            for elem in result_elements:
                try:
                    # Extract title and URL from the link
                    title_elem = elem.xpath('.//a[@class="result__a"]')
                    if not title_elem:
                        continue
                        
                    title = title_elem[0].text_content().strip()
                    url = title_elem[0].get('href', '')
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('.//a[@class="result__snippet"]')
                    description = ''
                    if snippet_elem:
                        description = snippet_elem[0].text_content().strip()
                    
                    # Only add if we have at least title and URL
                    if title and url:
                        results.append({
                            'title': title,
                            'url': url,
                            'description': description
                        })
                        
                except (AttributeError, IndexError, KeyError, TypeError):
                    # Skip malformed results
                    continue
            
        except requests.RequestException as e:
            # Network or HTTP errors
            raise Exception(f"Failed to query DuckDuckGo: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse DuckDuckGo results: {e}")
        
        return results
