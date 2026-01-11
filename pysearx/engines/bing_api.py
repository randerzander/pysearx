"""
Bing API-based search engine implementation for pysearx.

This implementation uses Microsoft's official Azure Cognitive Services
Bing Web Search API, which provides reliable search results without
CAPTCHA or bot blocking issues.

NOTE: This engine requires:
1. An Azure subscription
2. A Bing Search API key from Azure Portal
3. The azure-cognitiveservices-search-websearch package

Free tier: 1,000 transactions/month
Pricing: https://azure.microsoft.com/en-us/pricing/details/cognitive-services/search-api/

Installation: pip install azure-cognitiveservices-search-websearch
"""

from typing import List, Dict, Any, Optional
from ..base import SearchEngine

try:
    from azure.cognitiveservices.search.websearch import WebSearchClient
    from msrest.authentication import CognitiveServicesCredentials
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    # Set to None for testing purposes
    WebSearchClient = None
    CognitiveServicesCredentials = None


class BingAPIEngine(SearchEngine):
    """
    Bing search engine using official Azure Cognitive Services API.
    
    This engine uses Microsoft's official Bing Web Search API, which
    provides reliable results without CAPTCHA or blocking issues.
    However, it requires an API key and has usage limits/costs.
    
    Requires:
        - pip install azure-cognitiveservices-search-websearch
        - Azure subscription with Bing Search API key
    
    Free tier: 1,000 transactions per month
    """
    
    def __init__(self, api_key: str, region: str = 'global'):
        """
        Initialize the Bing API engine.
        
        Args:
            api_key: Your Bing Search API key from Azure Portal
            region: Azure region endpoint (default: 'global')
                   Use 'global' for https://api.bing.microsoft.com
                   
        Raises:
            ImportError: If azure-cognitiveservices-search-websearch is not installed
            ValueError: If api_key is not provided
        """
        if not AZURE_AVAILABLE:
            raise ImportError(
                "The 'azure-cognitiveservices-search-websearch' package is required for BingAPIEngine. "
                "Install it with: pip install azure-cognitiveservices-search-websearch"
            )
        
        if not api_key:
            raise ValueError(
                "Bing API key is required. "
                "Get your key from: https://portal.azure.com/"
            )
        
        self.name = 'Bing-API'
        self.api_key = api_key
        self.region = region
        
        # Initialize the Azure client
        credentials = CognitiveServicesCredentials(api_key)
        
        # Set endpoint based on region
        if region == 'global':
            endpoint = 'https://api.bing.microsoft.com'
        else:
            endpoint = f'https://api-{region}.cognitive.microsoft.com'
        
        self.client = WebSearchClient(
            credentials=credentials,
            endpoint=endpoint
        )
        
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Bing using the official Azure API.
        
        Args:
            query: The search query string
            **kwargs: Additional parameters:
                - market: Market code (e.g., 'en-US', 'en-GB')
                - count: Number of results (default: 20, max: 50)
                - offset: Pagination offset
                
        Returns:
            List of result dictionaries with title, url, and description
        """
        results = []
        
        try:
            # Extract optional parameters
            market = kwargs.get('market', 'en-US')
            count = kwargs.get('count', 20)
            offset = kwargs.get('offset', 0)
            
            # Make the API request
            response = self.client.web.search(
                query=query,
                count=min(count, 50),  # Max 50 results per request
                offset=offset,
                market=market,
                response_filter=['Webpages'],
                safe_search='Moderate'
            )
            
            # Extract web pages from response
            if hasattr(response, 'web_pages') and response.web_pages:
                for result in response.web_pages.value:
                    results.append({
                        'title': result.name,
                        'url': result.url,
                        'description': result.snippet if hasattr(result, 'snippet') else ''
                    })
                    
        except Exception as e:
            # Re-raise with more context
            raise Exception(f"Failed to query Bing API: {e}")
        
        return results


# Helper function to check if API engine is available
def is_available() -> bool:
    """
    Check if the Bing API engine is available.
    
    Returns:
        True if azure package is installed, False otherwise
    """
    return AZURE_AVAILABLE


# Example usage documentation
USAGE_EXAMPLE = """
Example usage of BingAPIEngine:

from pysearx.engines.bing_api import BingAPIEngine

# Initialize with your API key
api_key = "YOUR_BING_API_KEY_HERE"
bing_api = BingAPIEngine(api_key=api_key)

# Search
results = bing_api.search("python programming")

for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Description: {result['description']}")
    print()

# Get API key from:
# 1. Sign up for Azure: https://azure.microsoft.com/
# 2. Create a Bing Search resource
# 3. Copy your API key from Azure Portal
"""
