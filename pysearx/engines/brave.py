"""
Brave search engine implementation for pysearx.

This is a simplified implementation that queries Brave Search
and parses the results.
"""

from typing import List, Dict, Any
import re
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
            List of result dictionaries with title, url, description (deprecated), and summary
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
            headers['Accept-Encoding'] = 'gzip, deflate'  # Disable brotli (causes decode errors)
            
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
            
            # Find result divs - Brave uses data-type="web" for organic results
            result_elements = tree.xpath('//div[@data-type="web"]')
            
            for elem in result_elements:
                try:
                    # Extract title from div with class containing "title"
                    title_elem = elem.xpath('.//div[contains(@class, "title")]')
                    if not title_elem:
                        continue
                    title = title_elem[0].text_content().strip()
                    
                    # Extract URL from cite tag
                    cite_elem = elem.xpath('.//cite')
                    if not cite_elem:
                        continue
                    
                    url = cite_elem[0].text_content().strip()
                    # Clean up URL - remove spaces and extra text
                    if url:
                        url = url.split()[0]  # Take first part before spaces
                        # Add https if not present
                        if not url.startswith('http'):
                            url = 'https://' + url
                    
                    if not url or url.startswith('#'):
                        continue
                    
                    # Extract description/snippet - try multiple selectors
                    description = ''
                    snippet_elem = elem.xpath('.//div[contains(@class, "description")]') or \
                                  elem.xpath('.//div[contains(@class, "generic-snippet")]') or \
                                  elem.xpath('.//p[contains(@class, "snippet")]')
                    
                    if snippet_elem:
                        description = snippet_elem[0].text_content().strip()
                        # Clean up - remove date prefixes like "3 days ago - "
                        description = re.sub(r'^\d+\s+(day|hour|minute|second|week|month|year)s?\s+ago\s*-\s*', '', description)
                    
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
                print(f"[{self.name}] Rate limit detected! Switching to proxy mode.")
                self._failed_without_proxy = True
                self._use_proxy = True
                self._handle_rate_limit()
            raise Exception(f"Failed to query Brave: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Brave results: {e}")
        
        # Request succeeded, reset rate limit state
        self._reset_rate_limit()
        return results
