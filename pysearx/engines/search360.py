"""
360 Search engine implementation for pysearx.

360 Search (360搜索, also known as Haosou) is a Chinese search engine.
"""

from typing import List, Dict, Any
import requests
from lxml import html
from ..base import SearchEngine, DEFAULT_USER_AGENT, DEFAULT_HEADERS


class Search360Engine(SearchEngine):
    """360 Search engine implementation."""
    
    def __init__(self):
        self.name = '360Search'
        self.base_url = 'https://www.so.com/s'
        self.timeout = 10
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search 360 for the given query.
        
        Args:
            query: The search query string
            **kwargs: Additional parameters (currently unused)
            
        Returns:
            List of result dictionaries with title, url, and description
        """
        results = []
        
        try:
            # Prepare the request
            params = {
                'q': query,
                'src': 'srp',
            }
            
            # Use realistic headers
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = 'https://www.so.com/'
            headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
            
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
            
            # Find result divs - 360 Search uses res-list class
            result_elements = tree.xpath('//li[contains(@class, "res-list")]') or \
                            tree.xpath('//div[contains(@class, "result")]')
            
            for elem in result_elements:
                try:
                    # Extract title and URL
                    link_elem = elem.xpath('.//h3/a | .//a[contains(@class, "title")]')
                    
                    if not link_elem:
                        continue
                    
                    url = link_elem[0].get('href', '')
                    if not url or url.startswith('#'):
                        continue
                    
                    # 360 may use redirect URLs, extract real URL if needed
                    data_url = link_elem[0].get('data-url', '')
                    if data_url:
                        url = data_url
                    
                    # Extract title
                    title_elem = elem.xpath('.//h3')
                    if not title_elem:
                        title = link_elem[0].text_content().strip()
                    else:
                        title = title_elem[0].text_content().strip()
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('.//p[@class="res-desc"] | .//div[@class="res-desc"] | .//p')
                    
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
            raise Exception(f"Failed to query 360 Search: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse 360 Search results: {e}")
        
        return results
