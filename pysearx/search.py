"""
Core search functionality for pysearx.

This module provides the main search() function and coordinates
search engine queries.
"""

from typing import List, Dict, Any, Optional
import threading
import logging
from .base import SearchEngine
from .engines.duckduckgo import DuckDuckGoEngine
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

# Configure logger for the search module
logger = logging.getLogger(__name__)


# Default engines to use
DEFAULT_ENGINES = [
    DuckDuckGoEngine(),
    GoogleEngine(),
    BingEngine(),
    BraveEngine(),
    StartpageEngine(),
    QwantEngine(),
    MojeekEngine(),
    YahooEngine(),
    YepEngine(),
    SearxEngine(),
    SwisscowsEngine(),
    MetagerEngine(),
    Search360Engine(),
    YandexEngine(),
]


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
