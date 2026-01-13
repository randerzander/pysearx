"""
Qwant search engine implementation for pysearx.

This is a simplified implementation that queries Qwant Lite HTML
and parses the results.
"""

from typing import List, Dict, Any
import requests
from lxml import html
from ..base import SearchEngine, RateLimitMixin, DEFAULT_USER_AGENT, DEFAULT_HEADERS, get_proxy_dict

try:
    from ..browser import fetch_with_browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class QwantEngine(RateLimitMixin, SearchEngine):
    """Qwant search engine implementation."""
    
    def __init__(self):
        RateLimitMixin.__init__(self)
        self.name = 'Qwant'
        self.base_url = 'https://lite.qwant.com/'
        self.timeout = 10
        self.use_browser = PLAYWRIGHT_AVAILABLE
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        # Check if we're currently rate limited
        self._check_rate_limit()
        
        """
        # Check if we're currently rate limited
        self._check_rate_limit()
        
        Search Qwant for the given query.
        
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
            if self.use_browser and PLAYWRIGHT_AVAILABLE:
                # Use Playwright
                from urllib.parse import urlencode
                params = {
                    'q': query,
                    'locale': 'en_us',
                    'l': 'en',
                    's': '0',
                    'p': '1',
                }
                url = f"{self.base_url}?{urlencode(params)}"
                response_content = fetch_with_browser(url, timeout=self.timeout * 1000)
                tree = html.fromstring(response_content)
            else:
                # Fallback to requests
                params = {
                    'q': query,
                    'locale': 'en_us',
                    'l': 'en',
                    's': '0',
                    'p': '1',
                }
                
                headers = DEFAULT_HEADERS.copy()
                headers['Referer'] = 'https://lite.qwant.com/'
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=headers,
                    proxies=get_proxy_dict(),
                    timeout=self.timeout
                )
                response.raise_for_status()
                tree = html.fromstring(response.content)
            
            # Find result articles
            result_elements = tree.xpath('//section/article')
            
            for elem in result_elements:
                try:
                    # Skip advertising elements
                    if elem.xpath("./span[contains(@class, 'tooltip')]"):
                        continue
                    
                    # Extract URL
                    url_elem = elem.xpath("./span[contains(@class, 'url')]")
                    if not url_elem:
                        continue
                    url = url_elem[0].text_content().strip()
                    
                    # Extract title
                    title_elem = elem.xpath('./h2/a')
                    if not title_elem:
                        continue
                    title = title_elem[0].text_content().strip()
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('./p')
                    description = ''
                    if snippet_elem:
                        description = snippet_elem[0].text_content().strip()
                    
                    # Only add if we have at least title and URL
                    if title and url:
                        # Ensure URL has protocol
                        if not url.startswith('http'):
                            url = 'https://' + url
                        
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
            raise Exception(f"Failed to query Qwant: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Qwant results: {e}")
        
        # Request succeeded, reset rate limit state
        self._reset_rate_limit()
        return results
