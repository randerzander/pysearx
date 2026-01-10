"""
Startpage search engine implementation for pysearx.

This is a simplified implementation that queries Startpage
and parses the results.
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


class StartpageEngine(SearchEngine):
    """Startpage search engine implementation."""
    
    def __init__(self):
        self.name = 'Startpage'
        self.base_url = 'https://www.startpage.com/sp/search'
        self.timeout = 10
        self.use_browser = PLAYWRIGHT_AVAILABLE
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Startpage for the given query.
        
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
                    'cat': 'web',
                }
                url = f"{self.base_url}?{urlencode(params)}"
                response_content = fetch_with_browser(url, timeout=self.timeout * 1000)
                tree = html.fromstring(response_content)
            else:
                # Fallback to requests
                params = {
                    'query': query,
                    'cat': 'web',
                }
                
                # Use realistic headers
                headers = DEFAULT_HEADERS.copy()
                headers['Referer'] = 'https://www.startpage.com/'
                
                # Make the request
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                tree = html.fromstring(response.content)
            
            # Find result sections - Startpage uses w-gl__result class
            result_elements = tree.xpath('//div[contains(@class, "w-gl__result")]') or \
                            tree.xpath('//section[contains(@class, "w-gl__result")]')
            
            for elem in result_elements:
                try:
                    # Extract title and URL
                    link_elem = elem.xpath('.//a[@class="w-gl__result-title"]') or \
                               elem.xpath('.//h3/a') or \
                               elem.xpath('.//a')
                    
                    if not link_elem:
                        continue
                    
                    url = link_elem[0].get('href', '')
                    if not url or url.startswith('#'):
                        continue
                    
                    # Extract title
                    title_elem = elem.xpath('.//h3') or \
                                elem.xpath('.//a[@class="w-gl__result-title"]')
                    
                    if not title_elem:
                        title = link_elem[0].text_content().strip()
                    else:
                        title = title_elem[0].text_content().strip()
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('.//p[@class="w-gl__description"]') or \
                                  elem.xpath('.//div[contains(@class, "description")]') or \
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
            # Network or HTTP errors
            raise Exception(f"Failed to query Startpage: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Startpage results: {e}")
        
        return results
