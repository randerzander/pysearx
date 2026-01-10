"""
Swisscows search engine implementation for pysearx.

Swisscows is a privacy-focused search engine from Switzerland.
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


class SwisscowsEngine(SearchEngine):
    """Swisscows search engine implementation."""
    
    def __init__(self):
        self.name = 'Swisscows'
        self.base_url = 'https://swisscows.com/web'
        self.timeout = 10
        self.use_browser = PLAYWRIGHT_AVAILABLE
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Swisscows for the given query.
        
        Args:
            query: The search query string
            **kwargs: Additional parameters (currently unused)
            
        Returns:
            List of result dictionaries with title, url, and description
        """
        results = []
        
        try:
            if self.use_browser and PLAYWRIGHT_AVAILABLE:
                # Use Playwright
                from urllib.parse import urlencode
                params = {
                    'query': query,
                    'region': 'en-US',
                }
                url = f"{self.base_url}?{urlencode(params)}"
                response_content = fetch_with_browser(url, timeout=self.timeout * 1000)
                tree = html.fromstring(response_content)
            else:
                # Fallback to requests
                params = {
                    'query': query,
                    'region': 'en-US',
                }
                
                headers = DEFAULT_HEADERS.copy()
                headers['Referer'] = 'https://swisscows.com/'
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                tree = html.fromstring(response.content)
            
            # Find result divs - Swisscows uses article tags for results
            result_elements = tree.xpath('//article[contains(@class, "web-result")]') or \
                            tree.xpath('//article') or \
                            tree.xpath('//div[contains(@class, "result")]')
            
            for elem in result_elements:
                try:
                    # Extract title and URL
                    link_elem = elem.xpath('.//a[contains(@class, "site-link")] | .//h2/a | .//a')
                    
                    if not link_elem:
                        continue
                    
                    url = link_elem[0].get('href', '')
                    if not url or url.startswith('#'):
                        continue
                    
                    # Extract title
                    title_elem = elem.xpath('.//h2 | .//div[contains(@class, "title")]')
                    if not title_elem:
                        title = link_elem[0].text_content().strip()
                    else:
                        title = title_elem[0].text_content().strip()
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('.//p[contains(@class, "description")] | .//p | .//div[contains(@class, "description")]')
                    
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
            raise Exception(f"Failed to query Swisscows: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Swisscows results: {e}")
        
        return results
