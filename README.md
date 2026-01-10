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
from pysearx.engines.duckduckgo import DuckDuckGoEngine

# Use only DuckDuckGo
engines = [DuckDuckGoEngine()]
results = search("web development", engines=engines)
```

## API Reference

### `search(query, engines=None, max_results=10)`

Main search function.

**Parameters:**
- `query` (str): The search query string
- `engines` (list, optional): List of SearchEngine instances to use. Defaults to built-in engines.
- `max_results` (int, optional): Maximum number of results to return. Default is 10.

**Returns:**
- List of dictionaries, each containing:
  - `title`: Result title (str)
  - `url`: Result URL (str)
  - `description`: Result description/snippet (str)
  - `engine`: Name of the engine that returned this result (str)

## Supported Search Engines

Currently supported:
- DuckDuckGo (via HTML interface)

## Extending with New Engines

To add a new search engine, create a class that inherits from `SearchEngine`:

```python
from pysearx.search import SearchEngine

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
