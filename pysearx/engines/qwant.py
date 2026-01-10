"""
Qwant search engine implementation for pysearx.

This is a simplified implementation that queries Qwant Lite HTML
and parses the results.
"""

from typing import List, Dict, Any
import requests
from lxml import html
from ..base import SearchEngine, DEFAULT_USER_AGENT


class QwantEngine(SearchEngine):
    """Qwant search engine implementation."""
    
    def __init__(self):
        self.name = 'Qwant'
        self.base_url = 'https://lite.qwant.com/'
        self.timeout = 10
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Qwant for the given query.
        
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
                'locale': 'en_us',
                'l': 'en',
                's': '0',  # safesearch off
                'p': '1',  # page number
            }
            
            headers = {
                'User-Agent': DEFAULT_USER_AGENT
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
                            'description': description
                        })
                        
                except (AttributeError, IndexError, KeyError, TypeError):
                    # Skip malformed results
                    continue
            
        except requests.RequestException as e:
            # Network or HTTP errors
            raise Exception(f"Failed to query Qwant: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Qwant results: {e}")
        
        return results
