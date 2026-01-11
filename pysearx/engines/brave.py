"""
Brave search engine implementation for pysearx.

This is a simplified implementation that queries Brave Search
and parses the results.
"""

from typing import List, Dict, Any
import requests
from lxml import html
from ..base import SearchEngine, RateLimitMixin, DEFAULT_USER_AGENT, DEFAULT_HEADERS, get_proxy_dict


class BraveEngine(RateLimitMixin, SearchEngine):
    """Brave search engine implementation with rate limit backoff and proxy fallback."""
    
    def __init__(self):
        RateLimitMixin.__init__(self)
        self.name = 'Brave'
        self.base_url = 'https://search.brave.com/search'
        self.timeout = 10
        self._use_proxy = False  # Start without proxy
        self._failed_without_proxy = False  # Track if direct connection failed
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Brave for the given query.
        
        Args:
            query: The search query string
            **kwargs: Additional parameters (currently unused)
            
        Returns:
            List of result dictionaries with title, url, and description
        """
        # Check if we're currently rate limited (skip if we're using proxy)
        if not self._use_proxy:
            self._check_rate_limit()
        
        results = []
        
        try:
            # Prepare the request
            params = {
                'q': query,
            }
            
            # Use realistic headers
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = 'https://search.brave.com/'
            headers['Accept-Encoding'] = 'identity'  # Avoid brotli compression issues
            
            # Decide whether to use proxy
            proxies = None
            if self._use_proxy or self._failed_without_proxy:
                proxies = get_proxy_dict()
                if proxies:
                    print(f"[{self.name}] Using proxy: {proxies['http']}")
            
            # Make the request
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                proxies=proxies,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # If we succeeded, we can reset the failed flag
            if self._failed_without_proxy and proxies:
                print(f"[{self.name}] Proxy worked! Continuing with proxies.")
                self._use_proxy = True
            
            # Parse HTML response
            tree = html.fromstring(response.content)
            
            # Find result divs - Brave uses specific result containers
            result_elements = tree.xpath('//div[@data-type="web"]') or \
                            tree.xpath('//div[contains(@class, "snippet")]')
            
            for elem in result_elements:
                try:
                    # Extract title and URL
                    link_elem = elem.xpath('.//a[@class="result-header"]') or \
                               elem.xpath('.//h4/a') or \
                               elem.xpath('.//a')
                    
                    if not link_elem:
                        continue
                    
                    # Get the first valid link
                    url = link_elem[0].get('href', '')
                    if not url or url.startswith('#'):
                        continue
                    
                    # Extract title
                    title_elem = elem.xpath('.//h4') or \
                                elem.xpath('.//div[@class="title"]')
                    if not title_elem:
                        # Try getting title from link text
                        title = link_elem[0].text_content().strip()
                    else:
                        title = title_elem[0].text_content().strip()
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('.//p[@class="snippet-description"]') or \
                                  elem.xpath('.//div[@class="snippet-description"]') or \
                                  elem.xpath('.//p')
                    
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
            error_str = str(e)
            # Check for rate limit
            if self._is_rate_limit_error(error_str):
                print(f"[{self.name}] Rate limit detected! Switching to proxy mode.")
                self._failed_without_proxy = True
                self._use_proxy = True
                self._handle_rate_limit()
            raise Exception(f"Failed to query Brave: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Brave results: {e}")
        
        return results
