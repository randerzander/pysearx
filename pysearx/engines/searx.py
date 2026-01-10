"""
SearX search engine implementation for pysearx.

This implementation queries other SearX instances for search results.
Default instance: searx.be
"""

from typing import List, Dict, Any
import requests
from lxml import html
from ..base import SearchEngine, DEFAULT_USER_AGENT, DEFAULT_HEADERS


class SearxEngine(SearchEngine):
    """SearX search engine implementation."""
    
    def __init__(self):
        self.name = 'SearX'
        # Default instance - users can create custom instances if needed
        self.instance_url = 'https://searx.be'
        self.base_url = f'{self.instance_url}/search'
        self.timeout = 10
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search SearX for the given query.
        
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
                'category_general': '1',
                'language': 'en',
                'time_range': '',
                'safesearch': '0',
                'theme': 'simple',
            }
            
            # Use realistic headers
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = self.instance_url
            
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
            
            # Find result divs - SearX uses article with result class
            result_elements = tree.xpath('//article[contains(@class, "result")]') or \
                            tree.xpath('//div[@class="result"]')
            
            for elem in result_elements:
                try:
                    # Extract title and URL
                    link_elem = elem.xpath('.//h3/a | .//h4/a | .//a[@class="url_wrapper"]')
                    
                    if not link_elem:
                        continue
                    
                    url = link_elem[0].get('href', '')
                    if not url or url.startswith('#'):
                        continue
                    
                    # Extract title
                    title_elem = elem.xpath('.//h3 | .//h4')
                    if not title_elem:
                        title = link_elem[0].text_content().strip()
                    else:
                        title = title_elem[0].text_content().strip()
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('.//p[@class="content"] | .//p | .//div[@class="content"]')
                    
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
            raise Exception(f"Failed to query SearX: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse SearX results: {e}")
        
        return results
