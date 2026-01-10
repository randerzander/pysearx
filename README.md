# pysearx

A plain Python library implementing generic search engine functionality without external services.

## Overview

pysearx is a simple, single-process Python library that provides a generic search engine implementation inspired by SearXNG. It allows you to search the web programmatically without spinning up any external processes or services.

## Features

- Simple API: just call `search(query)` to get results
- Single-process execution - no threading or multiprocessing
- Returns results as a list of dictionaries with `title`, `url`, and `description`
- Support for multiple search engines
- Easy to extend with new search engines

## Installation

```bash
pip install -e .
```

## Requirements

- Python >= 3.7
- requests >= 2.25.0
- lxml >= 4.6.0

## Usage

Basic usage:

```python
from pysearx import search

# Search for a query
results = search("python programming")

# Process results
for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Description: {result['description']}")
    print(f"Engine: {result['engine']}")
    print()
```

Limit the number of results:

```python
from pysearx import search

# Get only top 5 results
results = search("machine learning", max_results=5)
```

Use specific search engines:

```python
from pysearx import search
from pysearx.engines.google import GoogleEngine
from pysearx.engines.bing import BingEngine

# Use only Google and Bing
engines = [GoogleEngine(), BingEngine()]
results = search("web development", engines=engines)
```

## API Reference

### `search(query, engines=None, max_results=10)`

Main search function.

**Parameters:**
- `query` (str): The search query string
- `engines` (list, optional): List of SearchEngine instances to use. If `None` (default), all 5 built-in engines are used (DuckDuckGo, Google, Bing, Brave, Startpage).
- `max_results` (int, optional): Maximum number of results to return. Default is 10.

**Returns:**
- List of dictionaries, each containing:
  - `title`: Result title (str)
  - `url`: Result URL (str)
  - `description`: Result description/snippet (str)
  - `engine`: Name of the engine that returned this result (str)

**Behavior:**
- Queries engines sequentially in order
- Aggregates results from all engines
- Automatically deduplicates by URL (first occurrence wins)
- Stops when `max_results` is reached or all engines exhausted
- If an engine fails, continues with remaining engines

## Supported Search Engines

Currently supported:
- DuckDuckGo (via HTML interface)
- Google
- Bing
- Brave Search
- Startpage

### How Multiple Engines Work

**By default, all 5 engines are used** when you call `search()` without specifying the `engines` parameter.

**Result Merging:**
- Engines are queried **sequentially** in the order listed above (DuckDuckGo, Google, Bing, Brave, Startpage)
- Results from all engines are **aggregated** into a single list
- **Deduplication** is performed by URL - if the same URL appears from multiple engines, only the first occurrence is kept
- The search continues until `max_results` is reached or all engines have been queried
- Each result includes an `engine` field indicating which search engine returned it

**Example:**
```python
from pysearx import search

# Uses all 5 engines, returns up to 10 results total
results = search("python programming", max_results=10)

# Results might come from different engines:
# results[0]['engine'] = 'DuckDuckGoEngine'
# results[1]['engine'] = 'DuckDuckGoEngine'
# results[2]['engine'] = 'GoogleEngine'
# results[3]['engine'] = 'BingEngine'
# etc.
```

To use only specific engines, pass them explicitly:
```python
from pysearx.engines.google import GoogleEngine

# Uses only Google
results = search("python", engines=[GoogleEngine()])
```

### Technical Implementation

**Engine Order:**
The default engine order (DuckDuckGo, Google, Bing, Brave, Startpage) is arbitrary. You can customize the order by explicitly passing engines in your preferred sequence.

**HTTP Requests:**
All searches are performed using plain HTTP requests via the `requests` library:
- GET requests for most engines (Google, Bing, Brave, Startpage)
- POST requests for DuckDuckGo
- HTML responses are parsed using `lxml`

**User-Agent Header:**
Yes, the library uses a browser-like User-Agent header to avoid being blocked:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

This mimics Chrome 120 on Windows 10 and is used across all search engines. Without this header, many search engines would block or return different results for automated requests. The User-Agent is defined in `pysearx/base.py` as `DEFAULT_USER_AGENT` and can be customized if needed.

## Extending with New Engines

To add a new search engine, create a class that inherits from `SearchEngine`:

```python
from pysearx import SearchEngine

class MyCustomEngine(SearchEngine):
    def search(self, query, **kwargs):
        # Implement search logic
        results = []
        # ... query the search engine and parse results ...
        return results  # List of dicts with title, url, description
```

## Example

See `example.py` for a complete usage example:

```bash
python example.py
```

## License

This project implements functionality inspired by SearXNG (https://github.com/searxng/searxng).

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
