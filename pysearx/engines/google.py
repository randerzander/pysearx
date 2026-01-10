"""
Google search engine implementation for pysearx.

This is a simplified implementation that queries Google
and parses the results.
"""

from typing import List, Dict, Any
import requests
from lxml import html
from ..base import SearchEngine


class GoogleEngine(SearchEngine):
    """Google search engine implementation."""
    
    def __init__(self):
        self.name = 'Google'
        self.base_url = 'https://www.google.com/search'
        self.timeout = 10
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Google for the given query.
        
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
                'num': 10,
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
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
            
            # Find result divs - Google uses various div structures
            # Try multiple selectors to handle different Google layouts
            result_elements = tree.xpath('//div[@class="g"]')
            if not result_elements:
                result_elements = tree.xpath('//div[contains(@class, "MjjYud")]')
            
            for elem in result_elements:
                try:
                    # Extract title and URL from the link
                    link_elem = elem.xpath('.//a[h3]')
                    if not link_elem:
                        link_elem = elem.xpath('.//a')
                    
                    if not link_elem:
                        continue
                    
                    url = link_elem[0].get('href', '')
                    if not url or url.startswith('#'):
                        continue
                    
                    # Extract title
                    title_elem = elem.xpath('.//h3')
                    if not title_elem:
                        continue
                    title = title_elem[0].text_content().strip()
                    
                    # Extract description/snippet
                    snippet_elems = elem.xpath('.//div[@data-sncf="1"]') or \
                                   elem.xpath('.//div[contains(@class, "VwiC3b")]') or \
                                   elem.xpath('.//span[contains(@class, "st")]')
                    
                    description = ''
                    if snippet_elems:
                        description = snippet_elems[0].text_content().strip()
                    
                    # Only add if we have at least title and URL
                    if title and url:
                        results.append({
                            'title': title,
                            'url': url,
                            'description': description
                        })
                        
                except Exception:
                    # Skip malformed results
                    continue
            
        except requests.RequestException as e:
            # Network or HTTP errors
            raise Exception(f"Failed to query Google: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Google results: {e}")
        
        return results
