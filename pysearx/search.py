"""
Core search functionality for pysearx.

This module provides the main search() function and coordinates
search engine queries.
"""

from typing import List, Dict, Any, Optional
import threading
import logging
from .base import SearchEngine
from .engines.google import GoogleEngine
from .engines.bing import BingEngine
from .engines.brave import BraveEngine
from .engines.startpage import StartpageEngine
from .engines.qwant import QwantEngine
from .engines.mojeek import MojeekEngine
from .engines.yahoo import YahooEngine
from .engines.yep import YepEngine
from .engines.searx import SearxEngine
from .engines.swisscows import SwisscowsEngine
from .engines.metager import MetagerEngine
from .engines.search360 import Search360Engine
from .engines.yandex import YandexEngine

# Try to use DuckDuckGo API engine (recommended), fallback to HTML scraping
try:
    from .engines.duckduckgo_api import DuckDuckGoAPIEngine, is_available
    if is_available():
        _ddg_engine = DuckDuckGoAPIEngine()
    else:
        # ddgs package not available, use HTML scraping
        from .engines.duckduckgo import DuckDuckGoEngine
        _ddg_engine = DuckDuckGoEngine()
except (ImportError, Exception):
    # Fall back to HTML scraping if API engine import fails
    from .engines.duckduckgo import DuckDuckGoEngine
    _ddg_engine = DuckDuckGoEngine()

# Configure logger for the search module
logger = logging.getLogger(__name__)


# Default engines to use
# Only 100% reliable engines are enabled by default
# DuckDuckGo API engine is used by default (falls back to HTML if ddgs not installed)
import os

DEFAULT_ENGINES = [
    _ddg_engine,        # DuckDuckGo API - 100% reliable, fast, 20 results
    YahooEngine(),      # Yahoo - 100% reliable, fast (0.85s), 10-15 results
    MojeekEngine(),     # Mojeek - 100% reliable, medium (1.4s), 10-12 results
]

# Conditionally enable Brave if proxies are available
# Brave works for ~27 queries, then auto-switches to proxies
if os.environ.get('PROXY_FILE'):
    DEFAULT_ENGINES.append(BraveEngine())  # 100% with proxies, 15-20 results

# Optional engines (uncomment to enable):
# DEFAULT_ENGINES.append(SearxEngine())  # Federated search, ~20% reliable, slow
#
# Engines disabled by default (require residential proxies):
# GoogleEngine(),      # Blocked without residential proxies
# BingEngine(),        # Blocked without residential proxies
# StartpageEngine(),   # Blocked without residential proxies
# QwantEngine(),       # Blocked without residential proxies
#
# Engines disabled (other reasons):
# Search360Engine(),   # Broken - missing RateLimitMixin
# YepEngine(),         # Returns 403 errors
# SwisscowsEngine(),   # Low reliability
# MetagerEngine(),     # Low reliability
# YandexEngine(),      # Low reliability


def search(query: str, engines: Optional[List[SearchEngine]] = None, 
           max_results: int = 10, parallel: bool = False) -> List[Dict[str, Any]]:
    """
    Search for a query across multiple search engines.
    
    This is the main API function for pysearx. It queries the specified
    search engines and returns aggregated results.
    
    Args:
        query: The search query string
        engines: List of SearchEngine instances to use. If None, uses defaults.
        max_results: Maximum number of results to return (default: 10)
        parallel: If True, queries all engines simultaneously using threading.
                 If False (default), queries engines sequentially.
        
    Returns:
        List of result dictionaries, each containing:
            - title: Result title (str)
            - url: Result URL (str)
            - description: Result description/snippet (str)
            - engine: Name of the engine that returned this result (str)
            
    Example:
        >>> results = search("python programming")
        >>> for result in results:
        ...     print(f"{result['title']}: {result['url']}")
        
        >>> # Use parallel mode for faster results
        >>> results = search("python programming", parallel=True)
    """
    if engines is None:
        engines = DEFAULT_ENGINES
    
    if parallel:
        return _search_parallel(query, engines, max_results)
    else:
        return _search_sequential(query, engines, max_results)


def _search_sequential(query: str, engines: List[SearchEngine], 
                      max_results: int) -> List[Dict[str, Any]]:
    """
    Sequential search implementation (original behavior).
    """
    all_results = []
    seen_urls = set()
    
    for engine in engines:
        try:
            engine_results = engine.search(query)
            
            # Add engine name and deduplicate by URL
            for result in engine_results:
                url = result.get('url', '')
                if url and url not in seen_urls:
                    result['engine'] = engine.__class__.__name__
                    all_results.append(result)
                    seen_urls.add(url)
                    
                    if len(all_results) >= max_results:
                        break
            
            if len(all_results) >= max_results:
                break
                
        except Exception as e:
            # Log error but continue with other engines
            logger.error(f"Error searching with {engine.__class__.__name__}: {e}")
            continue
    
    return all_results[:max_results]


def _search_parallel(query: str, engines: List[SearchEngine], 
                    max_results: int) -> List[Dict[str, Any]]:
    """
    Parallel search implementation using threading.
    
    Queries all engines simultaneously and aggregates results.
    
    Note: All threads run to completion. The max_results limit is applied
    after all results are collected. This means all engines complete their
    queries even if enough results are found early. This is a trade-off
    for the simplicity and speed benefit of parallel execution.
    """
    results_lock = threading.Lock()
    all_results = []
    seen_urls = set()
    
    def search_engine(engine: SearchEngine):
        """Thread worker function to search a single engine."""
        try:
            engine_results = engine.search(query)
            
            # Add engine name and deduplicate by URL
            with results_lock:
                for result in engine_results:
                    url = result.get('url', '')
                    if url and url not in seen_urls:
                        result['engine'] = engine.__class__.__name__
                        all_results.append(result)
                        seen_urls.add(url)
                        
        except Exception as e:
            # Log error but continue with other engines
            logger.error(f"Error searching with {engine.__class__.__name__}: {e}")
    
    # Create and start threads for each engine
    threads = []
    for engine in engines:
        thread = threading.Thread(target=search_engine, args=(engine,))
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    return all_results[:max_results]
