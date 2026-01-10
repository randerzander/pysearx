"""
pysearx - A plain Python library for generic web search

This library provides a simple API for searching the web across multiple
search engines without spinning up any external processes.

Basic usage:
    from pysearx import search
    
    results = search("python programming")
    for result in results:
        print(f"{result['title']}: {result['url']}")
"""

from .search import search
from .base import SearchEngine

__version__ = '0.1.0'
__all__ = ['search', 'SearchEngine']
