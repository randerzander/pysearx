"""
MetaGer search engine implementation for pysearx.

MetaGer is a privacy-focused metasearch engine from Germany.
"""

from typing import List, Dict, Any
from urllib.parse import urlparse
import requests
from lxml import html
from ..base import SearchEngine, DEFAULT_USER_AGENT, DEFAULT_HEADERS


class MetagerEngine(SearchEngine):
    """MetaGer search engine implementation."""
    
    def __init__(self):
        self.name = 'MetaGer'
        self.base_url = 'https://metager.org/meta/meta.ger3'
        self.timeout = 10
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search MetaGer for the given query.
        
        Args:
            query: The search query string
            **kwargs: Additional parameters (currently unused)
            
        Returns:
            List of result dictionaries with title, url, and description
        """
        results = []
        
        try:
            # Prepare the request - MetaGer uses POST
            data = {
                'eingabe': query,
                'encoding': 'utf8',
                'lang': 'en',
                'focus': 'web',
            }
            
            # Use realistic headers
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = 'https://metager.org/'
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            
            # Make the request
            response = requests.post(
                self.base_url,
                data=data,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse HTML response
            tree = html.fromstring(response.content)
            
            # Find result divs - MetaGer uses result-* classes
            result_elements = tree.xpath('//section[contains(@class, "result-")]') or \
                            tree.xpath('//div[contains(@class, "result")]') or \
                            tree.xpath('//li[contains(@class, "result")]')
            
            for elem in result_elements:
                try:
                    # Extract title and URL
                    link_elem = elem.xpath('.//a[@class="result-link"] | .//h2/a | .//h3/a | .//a')
                    
                    if not link_elem:
                        continue
                    
                    url = link_elem[0].get('href', '')
                    if not url or url.startswith('#'):
                        continue
                    
                    # MetaGer may use proxy URLs, extract real URL if needed
                    # Check if this is a MetaGer proxy URL by parsing the domain
                    try:
                        parsed_url = urlparse(url)
                        # Only process if this is explicitly a metager.org URL with /click path
                        if parsed_url.netloc == 'metager.org' and '/click' in parsed_url.path:
                            # Try to extract the actual URL from data attributes
                            real_url = link_elem[0].get('data-url', '')
                            if real_url and real_url.startswith('http'):
                                url = real_url
                    except ValueError:
                        # If URL parsing fails, just use the original URL
                        pass
                    
                    # Extract title
                    title_elem = elem.xpath('.//h2 | .//h3 | .//span[contains(@class, "title")]')
                    if not title_elem:
                        title = link_elem[0].text_content().strip()
                    else:
                        title = title_elem[0].text_content().strip()
                    
                    # Extract description/snippet
                    snippet_elem = elem.xpath('.//p[@class="description"] | .//p | .//div[@class="description"]')
                    
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
            raise Exception(f"Failed to query MetaGer: {e}")
        except Exception as e:
            # Parsing or other errors
            raise Exception(f"Failed to parse MetaGer results: {e}")
        
        return results
