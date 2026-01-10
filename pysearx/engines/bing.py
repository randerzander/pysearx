"""
Bing search engine implementation for pysearx.

This is a simplified implementation that queries Bing
and parses the results.
"""

from typing import List, Dict, Any
import requests
from lxml import html
from ..base import SearchEngine


class BingEngine(SearchEngine):
    """Bing search engine implementation."""
    
    def __init__(self):
        self.name = 'Bing'
        self.base_url = 'https://www.bing.com/search'
        self.timeout = 10
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Bing for the given query.
        
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
                'count': 10,
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
            
            # Find result items - Bing uses li.b_algo
            result_elements = tree.xpath('//li[@class="b_algo"]')
            if not result_elements:
                result_elements = tree.xpath('//li[contains(@class, "b_algo")]')
            
            for elem in result_elements:
                try:
                    # Extract title and URL from the h2/a element
                    link_elem = elem.xpath('.//h2/a')
                    if not link_elem:
                        continue
                    
                    title = link_elem[0].text_content().strip()
                    url = link_elem[0].get('href', '')
                    
                    if not title or not url:
                        continue
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('.//p[@class="b_lineclamp4 b_algoSlug"]') or \
                                  elem.xpath('.//div[@class="b_caption"]//p') or \
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
                        
                except Exception:
                    # Skip malformed results
                    continue
            
        except requests.RequestException as e:
            # Network or HTTP errors
            raise Exception(f"Failed to query Bing: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Bing results: {e}")
        
        return results
