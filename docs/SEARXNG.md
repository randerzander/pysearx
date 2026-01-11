# SearXNG Integration for pysearx

This document describes the SearXNG search engine integration for pysearx.

## Overview

SearXNG is a free, privacy-respecting metasearch engine that aggregates results from multiple search engines without tracking users. The pysearx SearXNG adapter makes HTTP requests to public SearXNG instances and parses results into the standard pysearx format.

## Features

- **JSON API Support**: Uses SearXNG's JSON API for reliable, structured results
- **HTML Parsing Fallback**: Can also parse HTML responses if JSON is not available
- **Custom Instances**: Support for any public or private SearXNG instance
- **Instance Discovery**: Utility to find the best available public instances from searx.space
- **Configurable Options**: Language, safe search, categories, and result limits

## Quick Start

### Basic Usage

```python
from pysearx.engines.searxng import SearxngEngine

# Create engine with default instance
engine = SearxngEngine()

# Search and get results
results = engine.search("python programming", num_results=10)

for result in results:
    print(f"{result['title']}")
    print(f"{result['url']}")
    print(f"{result['description']}\n")
```

### Using Custom Instance

```python
from pysearx.engines.searxng import SearxngEngine

# Use a specific instance
engine = SearxngEngine(instance_url="https://searx.tiekoetter.com")

results = engine.search("machine learning")
```

### Finding Best Instance

```python
from pysearx.engines.searxng import SearxngEngine
from utils.get_searxng_instances import get_best_instance

# Get the best performing instance
instance_url = get_best_instance()
engine = SearxngEngine(instance_url=instance_url)

results = engine.search("artificial intelligence")
```

## Utility: Getting SearXNG Instances

The `utils/get_searxng_instances.py` script fetches and filters public SearXNG instances from searx.space.

### Command Line Usage

```bash
python utils/get_searxng_instances.py
```

Output:
```
Fetching SearXNG instances from searx.space...

Found 68 working SearXNG instances:

URL                                                Success %    Response (s)    TLS Grade 
------------------------------------------------------------------------------------------
https://searx.lunar.icu/                           100.0        0.037           E         
https://priv.au/                                   100.0        0.038           A+        
...

Best instance: https://searx.lunar.icu/
```

### Programmatic Usage

```python
from utils.get_searxng_instances import (
    fetch_instances,
    get_working_instances,
    get_best_instance
)

# Get all working instances
instances = get_working_instances(
    min_success_rate=90.0,
    require_https=True,
    exclude_cloudflare=True
)

# Get the best instance
best = get_best_instance()

# Get raw data
all_data = fetch_instances()
```

## Search Options

The `search()` method accepts these optional parameters:

- **num_results** (int): Maximum number of results to return
- **language** (str): Language code (default: 'en')
- **safesearch** (int): Safe search level 0-2 (default: 0)
  - 0: None
  - 1: Moderate
  - 2: Strict
- **category** (str): Search category (default: 'general')
  - Options: general, images, videos, news, music, files, etc.

### Example with Options

```python
engine = SearxngEngine()

results = engine.search(
    "python tutorials",
    num_results=20,
    language='en',
    safesearch=1,
    category='general'
)
```

## Result Format

Each result is a dictionary with:

```python
{
    'title': str,        # Page title
    'url': str,          # Page URL
    'description': str   # Snippet/description (may be empty)
}
```

## Implementation Details

### JSON API (Default)

The engine uses SearXNG's JSON API by default (`format=json` parameter), which provides:
- Structured, reliable data
- Consistent parsing across different themes
- Better performance
- Easier error handling

### HTML Parsing (Fallback)

If JSON is disabled (`use_json=False`), the engine falls back to HTML parsing:
- Uses lxml for robust parsing
- Supports multiple SearXNG themes
- XPath selectors for finding result elements

### Error Handling

The engine handles several error conditions:
- Network failures
- HTTP errors (403, 429, 500, etc.)
- JSON/HTML parsing errors
- Missing required fields

Errors are raised as exceptions with descriptive messages.

## Rate Limiting

Public SearXNG instances may implement rate limiting. Strategies:

1. **Use Multiple Instances**: Rotate through several instances
2. **Add Delays**: Space out requests
3. **Self-Host**: Run your own SearXNG instance

### Fallback Pattern

```python
from utils.get_searxng_instances import get_working_instances

instances = get_working_instances()[:5]  # Top 5

for instance in instances:
    try:
        engine = SearxngEngine(instance_url=instance['url'])
        results = engine.search("query")
        break  # Success
    except:
        continue  # Try next
```

## Configuration

### Constructor Options

```python
SearxngEngine(
    instance_url=None,    # Custom instance URL
    use_json=True         # Use JSON API vs HTML parsing
)
```

### Instance Requirements

A SearXNG instance should:
- Be publicly accessible (unless using private instance)
- Support HTTPS (recommended)
- Return HTTP 200 status
- Have JSON API enabled (for use_json=True)

## Examples

See `example_searxng.py` for complete examples:

```bash
python example_searxng.py
```

## Testing

Run the test suite:

```bash
python test_searxng.py
```

Note: Tests may fail if instances are rate limiting or unavailable.

## Troubleshooting

### "403 Forbidden" Error

The instance is blocking requests. Try:
- Different instance
- Add delays between requests
- Check User-Agent header

### "Too Many Requests" Error

Rate limited. Solutions:
- Use different instance
- Implement backoff/retry
- Self-host instance

### No Results Returned

Possible causes:
- Instance is down
- Parsing error
- Query returned no results

Check by visiting the instance URL in browser.

## Related Files

- `pysearx/engines/searxng.py` - Main engine implementation
- `utils/get_searxng_instances.py` - Instance discovery utility
- `example_searxng.py` - Usage examples
- `test_searxng.py` - Test suite

## References

- [SearXNG Documentation](https://docs.searxng.org/)
- [SearXNG GitHub](https://github.com/searxng/searxng)
- [searx.space](https://searx.space/) - Public instance list
- [SearXNG Search API](https://docs.searxng.org/dev/search_api.html)
