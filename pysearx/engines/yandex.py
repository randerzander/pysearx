"""
Yandex search engine implementation for pysearx.

Yandex is a Russian search engine and technology company.
"""

from typing import List, Dict, Any
import requests
from lxml import html
from ..base import SearchEngine, DEFAULT_USER_AGENT, DEFAULT_HEADERS


class YandexEngine(SearchEngine):
    """Yandex search engine implementation."""
    
    def __init__(self):
        self.name = 'Yandex'
        self.base_url = 'https://yandex.com/search/'
        self.timeout = 10
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Yandex for the given query.
        
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
                'text': query,
                'lr': '84',  # English region
            }
            
            # Use realistic headers
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = 'https://yandex.com/'
            
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
            
            # Find result divs - Yandex uses serp-item class
            result_elements = tree.xpath('//li[contains(@class, "serp-item")]') or \
                            tree.xpath('//div[contains(@class, "serp-item")]') or \
                            tree.xpath('//div[contains(@class, "organic")]')
            
            for elem in result_elements:
                try:
                    # Extract title and URL
                    link_elem = elem.xpath('.//h2/a | .//a[contains(@class, "title")]') or \
                               elem.xpath('.//a[contains(@class, "OrganicTitle")]')
                    
                    if not link_elem:
                        continue
                    
                    url = link_elem[0].get('href', '')
                    if not url or url.startswith('#'):
                        continue
                    
                    # Yandex sometimes uses relative URLs, make them absolute
                    if url.startswith('/'):
                        url = 'https://yandex.com' + url
                    
                    # Extract title
                    title_elem = elem.xpath('.//h2 | .//a[contains(@class, "OrganicTitle")]')
                    if not title_elem:
                        title = link_elem[0].text_content().strip()
                    else:
                        title = title_elem[0].text_content().strip()
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('.//div[contains(@class, "text-container")] | .//div[contains(@class, "abstract")]') or \
                                  elem.xpath('.//div[contains(@class, "OrganicText")]')
                    
                    description = ''
                    if snippet_elem:
                        description = snippet_elem[0].text_content().strip()
                    
                    # Only add if we have at least title and URL
                    if title and url and not url.startswith('#'):
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
            raise Exception(f"Failed to query Yandex: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse Yandex results: {e}")
        
        return results
