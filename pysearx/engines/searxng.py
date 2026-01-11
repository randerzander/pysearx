"""
SearXNG search engine implementation for pysearx.

This implementation queries public SearXNG instances for search results.
SearXNG is a privacy-respecting metasearch engine.
"""

from typing import List, Dict, Any, Optional
import requests
from lxml import html
from ..base import SearchEngine, DEFAULT_USER_AGENT, DEFAULT_HEADERS


class SearxngEngine(SearchEngine):
    """SearXNG search engine implementation."""
    
    def __init__(self, instance_url: Optional[str] = None, use_json: bool = True):
        """
        Initialize SearXNG engine.
        
        Args:
            instance_url: Custom SearXNG instance URL. If None, uses default.
            use_json: Use JSON API instead of HTML parsing (default: True, more reliable)
        """
        self.name = 'SearXNG'
        self.instance_url = instance_url or 'https://searx.be'
        # Remove trailing slash if present
        self.instance_url = self.instance_url.rstrip('/')
        self.base_url = f'{self.instance_url}/search'
        self.timeout = 15
        self.use_json = use_json
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search SearXNG for the given query.
        
        Args:
            query: The search query string
            **kwargs: Additional parameters
                - num_results: Maximum number of results to return (default: all)
                - language: Language code (default: 'en')
                - safesearch: Safe search level 0-2 (default: 0)
                - category: Search category (default: 'general')
            
        Returns:
            List of result dictionaries with title, url, and description
        """
        results = []
        
        # Extract optional parameters
        language = kwargs.get('language', 'en')
        safesearch = kwargs.get('safesearch', 0)
        category = kwargs.get('category', 'general')
        num_results = kwargs.get('num_results', None)
        
        try:
            # Prepare the request parameters
            params = {
                'q': query,
                'language': language,
                'safesearch': str(safesearch),
                'categories': category,
            }
            
            # Add format parameter if using JSON
            if self.use_json:
                params['format'] = 'json'
            
            # Use realistic headers
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = self.instance_url
            
            # Make the request
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Parse the response
            if self.use_json:
                results = self._parse_json_results(response.json())
            else:
                results = self._parse_html_results(response.content)
            
            # Limit results if requested
            if num_results and num_results > 0:
                results = results[:num_results]
            
        except requests.RequestException as e:
            raise Exception(f"Failed to query SearXNG at {self.instance_url}: {e}")
        except Exception as e:
            raise Exception(f"Failed to parse SearXNG results: {e}")
        
        return results
    
    def _parse_json_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse search results from JSON response.
        
        Args:
            data: JSON response data
            
        Returns:
            List of parsed result dictionaries
        """
        results = []
        
        # Get results array from JSON
        json_results = data.get('results', [])
        
        for item in json_results:
            try:
                title = item.get('title', '').strip()
                url = item.get('url', '').strip()
                description = item.get('content', '').strip()
                
                # Skip invalid results
                if not title or not url:
                    continue
                
                results.append({
                    'title': title,
                    'url': url,
                    'description': description
                })
            except (AttributeError, KeyError, TypeError):
                continue
        
        return results
    
    def _parse_html_results(self, content: bytes) -> List[Dict[str, Any]]:
        """
        Parse search results from HTML content.
        
        Args:
            content: HTML content from the response
            
        Returns:
            List of parsed result dictionaries
        """
        results = []
        tree = html.fromstring(content)
        
        # SearXNG uses <article class="result"> for search results
        # Try multiple selectors for compatibility with different themes
        result_elements = (
            tree.xpath('//article[contains(@class, "result")]') or
            tree.xpath('//div[contains(@class, "result")]') or
            tree.xpath('//div[@class="result"]')
        )
        
        for elem in result_elements:
            try:
                result = self._parse_result_element(elem)
                if result:
                    results.append(result)
            except (AttributeError, IndexError, KeyError, TypeError):
                # Skip malformed results
                continue
        
        return results
    
    def _parse_result_element(self, elem) -> Optional[Dict[str, Any]]:
        """
        Parse a single result element.
        
        Args:
            elem: lxml element for a single result
            
        Returns:
            Dictionary with title, url, and description, or None if invalid
        """
        # Extract URL - try multiple selectors
        link_elem = (
            elem.xpath('.//h3/a[@href]') or
            elem.xpath('.//h4/a[@href]') or
            elem.xpath('.//a[@class="url_wrapper"]') or
            elem.xpath('.//a[@href]')
        )
        
        if not link_elem:
            return None
        
        url = link_elem[0].get('href', '').strip()
        
        # Skip invalid URLs
        if not url or url.startswith('#') or url.startswith('javascript:'):
            return None
        
        # Extract title - try from heading or link text
        title = ''
        title_elem = elem.xpath('.//h3 | .//h4')
        if title_elem:
            title = title_elem[0].text_content().strip()
        else:
            title = link_elem[0].text_content().strip()
        
        # Extract description/snippet
        description = ''
        snippet_elem = (
            elem.xpath('.//p[@class="content"]') or
            elem.xpath('.//div[@class="content"]') or
            elem.xpath('.//p[contains(@class, "description")]') or
            elem.xpath('.//p') or
            elem.xpath('.//div[@class="snippet"]')
        )
        
        if snippet_elem:
            description = snippet_elem[0].text_content().strip()
        
        # Only return if we have at least title and URL
        if not title or not url:
            return None
        
        return {
            'title': title,
            'url': url,
            'description': description
        }
