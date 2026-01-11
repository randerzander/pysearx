"""
Yahoo search engine implementation for pysearx.

This is a simplified implementation that queries Yahoo Search
and parses the results.
"""

from typing import List, Dict, Any
import requests
from lxml import html
from urllib.parse import unquote
from ..base import SearchEngine, RateLimitMixin, DEFAULT_USER_AGENT, DEFAULT_HEADERS


class YahooEngine(RateLimitMixin, SearchEngine):
    """Yahoo search engine implementation."""
    
    def __init__(self):
        RateLimitMixin.__init__(self)
        self.name = 'Yahoo'
        self.base_url = 'https://search.yahoo.com/search'
        self.timeout = 10
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Yahoo for the given query.
        
        Args:
            query: The search query string
            **kwargs: Additional parameters (currently unused)
            
        Returns:
            List of result dictionaries with title, url, and description
        """
        # Check if we're currently rate limited
        self._check_rate_limit()
        
        results = []
        
        try:
            # Prepare the request
            params = {
                'p': query,
                'iscqry': '',  # Required for first page results
            }
            
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = 'https://search.yahoo.com/'
            
            # Yahoo uses cookies for settings
            cookies = {
                'sB': 'v=1&vm=p&fl=1&vl=lang_en&pn=10&rw=new&userset=1'
            }
            
            # Make the request
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse HTML response
            tree = html.fromstring(response.content)
            
            # Find result elements - Yahoo uses algo-sr class
            result_elements = tree.xpath('//div[contains(@class,"algo-sr")]')
            
            for elem in result_elements:
                try:
                    # Extract URL - try both xpaths as Yahoo has different layouts
                    url_elem = elem.xpath('.//div[contains(@class,"compTitle")]/a/@href')
                    if not url_elem:
                        url_elem = elem.xpath('.//div[contains(@class,"compTitle")]/h3/a/@href')
                    
                    if not url_elem:
                        continue
                    
                    url = url_elem[0]
                    # Parse Yahoo tracking URL to get actual URL
                    url = self._parse_url(url)
                    
                    # Extract title
                    title_elem = elem.xpath('.//div[contains(@class,"compTitle")]/a/h3/span')
                    if not title_elem:
                        title_elem = elem.xpath('.//div[contains(@class,"compTitle")]/h3/a/@aria-label')
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem[0]
                    if hasattr(title, 'text_content'):
                        title = title.text_content().strip()
                    else:
                        title = str(title).strip()
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('.//div[contains(@class, "compText")]')
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
                self._handle_rate_limit()
            raise Exception(f"Failed to query Yahoo: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Yahoo results: {e}")
        
        return results
    
    def _parse_url(self, url_string: str) -> str:
        """Remove Yahoo-specific tracking URL to get the actual URL."""
        endings = ['/RS', '/RK']
        endpositions = []
        
        # Find the position of /RU= marker
        ru_pos = url_string.find('/RU=')
        if ru_pos == -1:
            return url_string
        
        # Find the actual URL after /RU=
        start = url_string.find('http', ru_pos + 1)
        
        for ending in endings:
            endpos = url_string.rfind(ending)
            if endpos > -1:
                endpositions.append(endpos)
        
        if start <= 0 or len(endpositions) == 0:
            return url_string
        
        end = min(endpositions)
        return unquote(url_string[start:end])
