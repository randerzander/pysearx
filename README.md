# pysearx

A plain Python library implementing generic search engine functionality without external services.

## 🆕 NEW: API-Based Engines (No CAPTCHA/Blocking)

**Avoid CAPTCHA and bot blocking issues** by using official API packages:
- ✅ **DuckDuckGo API** - Free, no API key required ([Quick Start](QUICKSTART_API_ENGINES.md))
- ⚠️ **Bing API** - Requires Azure API key, free tier available

See [QUICKSTART_API_ENGINES.md](QUICKSTART_API_ENGINES.md) for setup and [SEARCH_PACKAGES_RESEARCH.md](SEARCH_PACKAGES_RESEARCH.md) for detailed research.

## Overview

pysearx is a simple, single-process Python library that provides a generic search engine implementation inspired by SearXNG. It allows you to search the web programmatically without spinning up any external processes or services.

## Features

- Simple API: just call `search(query)` to get results
- Sequential or parallel execution modes (parallel uses threading for faster results)
- Returns results as a list of dictionaries with `title`, `url`, and `description`
- Support for multiple search engines (14 built-in: DuckDuckGo, Google, Bing, Brave, Startpage, Qwant, Mojeek, Yahoo, Yep, SearX, Swisscows, MetaGer, 360Search, Yandex)
- **NEW**: API-based engines that avoid CAPTCHA/blocking (DuckDuckGo, Bing)
- Easy to extend with new search engines

## Installation

Basic installation:
```bash
pip install -e .
```

**Recommended**: Install with DuckDuckGo API support (avoids CAPTCHA/blocking):
```bash
pip install -e .[ddg-api]
```

Install with all optional API integrations:
```bash
pip install -e .[all-apis]
```

## Requirements

**Core requirements:**
- Python >= 3.7
- requests >= 2.25.0
- lxml >= 4.6.0

**Optional (recommended):**
- ddgs >= 9.0.0 - DuckDuckGo API support (no CAPTCHA/blocking issues)

**Optional (requires API key):**
- azure-cognitiveservices-search-websearch >= 2.0.0 - Bing API support

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

Use parallel mode for faster searches:

```python
from pysearx import search

# Search all engines simultaneously using threading
results = search("python programming", parallel=True)

# Parallel mode is especially useful with all 9 engines
# to get results faster
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

**Recommended**: Use API-based engines to avoid CAPTCHA/blocking:

```python
from pysearx import search
from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine

# Use DuckDuckGo API (no CAPTCHA, more reliable)
# Requires: pip install pysearx[ddg-api]
ddg_api = DuckDuckGoAPIEngine()
results = search("python programming", engines=[ddg_api])
```

For Bing API (requires Azure API key):

```python
from pysearx.engines.bing_api import BingAPIEngine

# Requires: pip install pysearx[bing-api]
# Get API key from: https://portal.azure.com/
bing_api = BingAPIEngine(api_key="YOUR_BING_API_KEY")
results = search("web development", engines=[bing_api])
```

## API Reference

### `search(query, engines=None, max_results=10, parallel=False)`

Main search function.

**Parameters:**
- `query` (str): The search query string
- `engines` (list, optional): List of SearchEngine instances to use. If `None` (default), all 14 built-in engines are used (DuckDuckGo, Google, Bing, Brave, Startpage, Qwant, Mojeek, Yahoo, Yep, SearX, Swisscows, MetaGer, 360Search, Yandex).
- `max_results` (int, optional): Maximum number of results to return. Default is 10.
- `parallel` (bool, optional): If `True`, queries all engines simultaneously using threading for faster results. If `False` (default), queries engines sequentially. Default is `False`.

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

### HTML-Based Engines (Default)

Currently supported:
- DuckDuckGo (via HTML interface)
- Google
- Bing
- Brave Search
- Startpage
- Qwant (via Lite interface)
- Mojeek
- Yahoo
- Yep (by Ahrefs)
- SearX (other SearX instances, default: searx.be)
- Swisscows
- MetaGer
- 360Search (Chinese search engine)
- Yandex

**Note**: HTML-based engines may encounter CAPTCHA or bot blocking issues. For better reliability, use API-based engines below.

### API-Based Engines (Recommended)

**DuckDuckGo API Engine** (`DuckDuckGoAPIEngine`) - **RECOMMENDED** ✅
- **Package**: `ddgs` (pip install pysearx[ddg-api])
- **Cost**: Free, no API key required
- **Reliability**: No CAPTCHA or blocking issues
- **Maintenance**: Well-maintained, active development
- **Use case**: Best choice for DuckDuckGo searches

```python
from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine
ddg = DuckDuckGoAPIEngine()
results = ddg.search("python programming")
```

**Bing API Engine** (`BingAPIEngine`) - Optional
- **Package**: `azure-cognitiveservices-search-websearch` (pip install pysearx[bing-api])
- **Cost**: Requires Azure API key (free tier: 1,000 requests/month)
- **Reliability**: Official Microsoft API, 100% reliable
- **Setup**: Requires Azure subscription and API key
- **Use case**: Enterprise applications needing guaranteed reliability

```python
from pysearx.engines.bing_api import BingAPIEngine
bing = BingAPIEngine(api_key="YOUR_API_KEY")
results = bing.search("python programming")
```

**See also**: `SEARCH_PACKAGES_RESEARCH.md` for detailed research findings on these packages.

### How Multiple Engines Work

**By default, all 14 engines are used** when you call `search()` without specifying the `engines` parameter.

**Sequential Mode (default, `parallel=False`):**
- Engines are queried **sequentially** in the order listed above (DuckDuckGo, Google, Bing, Brave, Startpage, Qwant, Mojeek, Yahoo, Yep, SearX, Swisscows, MetaGer, 360Search, Yandex)
- Results from all engines are **aggregated** into a single list
- **Deduplication** is performed by URL - if the same URL appears from multiple engines, only the first occurrence is kept
- The search continues until `max_results` is reached or all engines have been queried
- Each result includes an `engine` field indicating which search engine returned it

**Parallel Mode (`parallel=True`):**
- All engines are queried **simultaneously** using threading
- Results are aggregated as they come in from each thread
- Same **deduplication** by URL is applied
- **Faster** overall search time since engines run in parallel
- Useful when querying all 14 engines to minimize total wait time

**Example:**
```python
from pysearx import search

# Sequential mode (default)
results = search("python programming", max_results=10)

# Parallel mode for faster results
results = search("python programming", max_results=10, parallel=True)

# Results might come from different engines:
# results[0]['engine'] = 'DuckDuckGoEngine'
# results[1]['engine'] = 'GoogleEngine'
# results[2]['engine'] = 'BingEngine'
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

## Performance

For detailed performance benchmarks and testing instructions, see [docs/performance.md](docs/performance.md).

You can run your own performance tests to evaluate engine performance in your environment:

```bash
python test_performance.py
```

This will test all 5 engines with 10 queries and provide detailed metrics including:
- Response times per engine
- Success/failure rates
- Rate limiting detection
- Performance statistics and comparisons

## License

This project implements functionality inspired by SearXNG (https://github.com/searxng/searxng).

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
