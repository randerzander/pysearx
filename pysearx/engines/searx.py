"""
SearX search engine implementation for pysearx.

This implementation queries public SearXNG instances with automatic rotation.
On first use, fetches instance list from searx.space and rotates through them.
Failed instances are automatically removed from the pool.
"""

from typing import List, Dict, Any, Optional
import requests
from lxml import html
from ..base import SearchEngine, DEFAULT_USER_AGENT, DEFAULT_HEADERS


class SearxEngine(SearchEngine):
    """SearX/SearXNG search engine implementation with automatic instance rotation."""
    
    # Class-level variables shared across all instances
    _instances: Optional[List[str]] = None
    _current_index: int = 0
    _instances_lock = None
    
    def __init__(self):
        self.name = 'SearX'
        self.timeout = 15
        
        # Initialize thread lock for thread-safe instance rotation
        if SearxEngine._instances_lock is None:
            import threading
            SearxEngine._instances_lock = threading.Lock()
        
        # Load instances on first initialization
        if SearxEngine._instances is None:
            self._load_instances()
    
    def _load_instances(self):
        """Load public SearXNG instances from searx.space."""
        try:
            # Import the utility function
            import sys
            import os
            # Add utils directory to path
            utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'utils')
            if utils_path not in sys.path:
                sys.path.insert(0, utils_path)
            
            from get_searxng_instances import get_working_instances
            
            # Get working instances with reasonable quality threshold
            instances_data = get_working_instances(
                min_success_rate=90.0,
                require_https=True,
                exclude_cloudflare=False  # Include cloudflare for more options
            )
            
            # Extract just the URLs
            SearxEngine._instances = [inst['url'].rstrip('/') for inst in instances_data]
            
            if not SearxEngine._instances:
                # Fallback to a known instance if fetch fails
                SearxEngine._instances = ['https://searx.be']
            
            print(f"[SearX] Loaded {len(SearxEngine._instances)} public instances")
            
        except Exception as e:
            # Fallback to default instance if anything fails
            print(f"[SearX] Failed to load instances: {e}")
            SearxEngine._instances = ['https://searx.be']
    
    def _get_next_instance(self) -> str:
        """Get the next instance URL from the rotation."""
        with SearxEngine._instances_lock:
            if not SearxEngine._instances:
                # Reload if list is empty
                self._load_instances()
            
            if not SearxEngine._instances:
                raise Exception("No SearX instances available")
            
            # Get current instance and increment
            instance = SearxEngine._instances[SearxEngine._current_index]
            SearxEngine._current_index = (SearxEngine._current_index + 1) % len(SearxEngine._instances)
            
            return instance
    
    def _remove_failed_instance(self, instance_url: str):
        """Remove a failed instance from the pool."""
        with SearxEngine._instances_lock:
            if instance_url in SearxEngine._instances:
                SearxEngine._instances.remove(instance_url)
                print(f"[SearX] Removed failed instance: {instance_url}")
                print(f"[SearX] {len(SearxEngine._instances)} instances remaining")
                
                # Adjust index if needed
                if SearxEngine._current_index >= len(SearxEngine._instances) and SearxEngine._instances:
                    SearxEngine._current_index = 0
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search SearX for the given query.
        
        Automatically rotates through available instances and removes failed ones.
        Retries with next instance on failure.
        
        Args:
            query: The search query string
            **kwargs: Additional parameters
                - num_results: Maximum number of results to return
                - format: 'json' or 'html' (default: 'json')
                - max_retries: Maximum instance retries (default: 3)
            
        Returns:
            List of result dictionaries with title, url, description (deprecated), and summary
        """
        # Get parameters
        num_results = kwargs.get('num_results', None)
        use_json = kwargs.get('format', 'json') == 'json'
        max_retries = kwargs.get('max_retries', 3)
        
        last_error = None
        
        # Try up to max_retries different instances
        for attempt in range(max_retries):
            # Get next instance to try
            instance_url = self._get_next_instance()
            
            try:
                if use_json:
                    results = self._search_json(instance_url, query)
                else:
                    results = self._search_html(instance_url, query)
                
                # Limit results if requested
                if num_results and num_results > 0:
                    results = results[:num_results]
                
                return results
                
            except Exception as e:
                last_error = e
                error_str = str(e)
                
                # Check if it's a client error (403, 429, etc) - remove instance
                if '403' in error_str or '429' in error_str or '401' in error_str:
                    self._remove_failed_instance(instance_url)
                # For other errors, just try next instance without removing
                
                # Continue to next instance
                continue
        
        # All retries failed
        if last_error:
            raise Exception(f"Failed to query SearX after {max_retries} attempts: {last_error}")
        else:
            raise Exception(f"Failed to query SearX after {max_retries} attempts")
    
    def _search_json(self, instance_url: str, query: str) -> List[Dict[str, Any]]:
        """Search using JSON API."""
        base_url = f'{instance_url}/search'
        
        params = {
            'q': query,
            'format': 'json',
            'language': 'en',
            'safesearch': '0',
        }
        
        headers = DEFAULT_HEADERS.copy()
        headers['Referer'] = instance_url
        
        response = requests.get(
            base_url,
            params=params,
            headers=headers,
            timeout=self.timeout,
            allow_redirects=True
        )
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('results', []):
            try:
                title = item.get('title', '').strip()
                url = item.get('url', '').strip()
                description = item.get('content', '').strip()
                
                if title and url:
                    results.append({
                        'title': title,
                        'url': url,
                        'description': description,  # deprecated, use summary
                        'summary': description
                    })
            except (AttributeError, KeyError, TypeError):
                continue
        
        return results
    
    def _search_html(self, instance_url: str, query: str) -> List[Dict[str, Any]]:
        """Search using HTML parsing (fallback)."""
        base_url = f'{instance_url}/search'
        
        params = {
            'q': query,
            'category_general': '1',
            'language': 'en',
            'safesearch': '0',
        }
        
        headers = DEFAULT_HEADERS.copy()
        headers['Referer'] = instance_url
        
        response = requests.get(
            base_url,
            params=params,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        # Parse HTML response
        tree = html.fromstring(response.content)
        results = []
        
        # Find result divs - SearX uses article with result class
        result_elements = (
            tree.xpath('//article[contains(@class, "result")]') or
            tree.xpath('//div[@class="result"]')
        )
        
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
                        'description': description,  # deprecated, use summary
                        'summary': description
                    })
                    
            except (AttributeError, IndexError, KeyError, TypeError):
                # Skip malformed results
                continue
        
        return results
