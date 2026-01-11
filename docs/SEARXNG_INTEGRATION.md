# SearXNG Integration Summary

## What Was Created

This implementation adds comprehensive SearXNG support to pysearx, including a utility to discover public instances and a search engine adapter that makes HTTP requests to SearXNG instances.

## Files Created

### 1. Core Engine Implementation
**File**: `pysearx/engines/searxng.py`
- Full-featured SearXNG search engine adapter
- Supports both JSON API (default) and HTML parsing
- Configurable instance URLs
- Comprehensive error handling
- Search options: language, safesearch, categories, result limits

### 2. Instance Discovery Utility
**File**: `utils/get_searxng_instances.py`
- Fetches public SearXNG instances from searx.space API
- Filters instances by success rate, HTTPS, network type
- Returns sorted list by performance
- Command-line interface to display instances
- Programmatic API for integration

### 3. Documentation
**File**: `docs/SEARXNG.md`
- Complete guide to using SearXNG with pysearx
- API reference
- Configuration options
- Examples and troubleshooting
- Rate limiting strategies

**File**: `utils/README.md`
- Documentation for utility scripts
- Usage examples

### 4. Examples and Tests
**File**: `example_searxng.py`
- Demonstrates various usage patterns
- Shows instance discovery
- Fallback strategies
- Search options

**File**: `test_searxng.py`
- Test suite for SearXNG engine
- Tests multiple instances
- Validates search functionality

### 5. Module Updates
**File**: `pysearx/engines/__init__.py`
- Added SearxngEngine to exports

**File**: `README.md`
- Updated to mention SearXNG support
- Updated engine count to 15

## Key Features

### SearXNG Engine (`SearxngEngine`)

```python
from pysearx.engines.searxng import SearxngEngine

# Initialize with default or custom instance
engine = SearxngEngine(instance_url="https://searx.tiekoetter.com")

# Search with options
results = engine.search(
    "query",
    num_results=10,
    language='en',
    safesearch=1,
    category='general'
)
```

**Features:**
- JSON API support (default, more reliable)
- HTML parsing fallback
- Custom instance URLs
- Full search customization
- Proper error handling

### Instance Discovery Utility

```python
from utils.get_searxng_instances import get_best_instance, get_working_instances

# Get best instance
best = get_best_instance()

# Get filtered list
instances = get_working_instances(
    min_success_rate=90.0,
    require_https=True,
    exclude_cloudflare=True
)
```

**Features:**
- Fetches from searx.space API
- Filters by multiple criteria
- Sorts by performance
- Returns detailed metadata
- Command-line interface

## Usage Examples

### Basic Search
```python
from pysearx.engines.searxng import SearxngEngine

engine = SearxngEngine()
results = engine.search("python tutorials", num_results=5)

for r in results:
    print(f"{r['title']}: {r['url']}")
```

### With Best Instance
```python
from pysearx.engines.searxng import SearxngEngine
from utils.get_searxng_instances import get_best_instance

engine = SearxngEngine(instance_url=get_best_instance())
results = engine.search("machine learning")
```

### List Instances
```bash
python utils/get_searxng_instances.py
```

## Implementation Details

### HTTP Requests
- Uses `requests` library
- Realistic headers to avoid detection
- Proper User-Agent strings
- Timeout handling (15s default)
- Follows redirects

### JSON API (Default Method)
- Uses `format=json` parameter
- Parses structured JSON response
- More reliable than HTML
- Consistent across themes
- Better performance

### HTML Parsing (Fallback)
- Uses `lxml` for parsing
- XPath selectors for robustness
- Supports multiple SearXNG themes
- Handles malformed results gracefully

### Error Handling
- Network errors (timeouts, DNS, etc.)
- HTTP errors (403, 429, 500, etc.)
- JSON/HTML parsing errors
- Missing required fields
- Descriptive error messages

## Testing

All components tested:
- ✓ Instance discovery from searx.space
- ✓ Engine initialization
- ✓ Custom instance configuration
- ✓ Module imports
- ✓ Example scripts

Note: Live search tests may fail due to rate limiting from public instances.

## Rate Limiting Considerations

Public SearXNG instances often implement rate limiting. Strategies:

1. **Multiple Instances**: The utility provides 68+ working instances
2. **Fallback Pattern**: Try multiple instances sequentially
3. **Delays**: Add delays between requests
4. **Self-Hosting**: Run your own SearXNG instance

## Integration with pysearx

The SearXNG engine follows the standard pysearx interface:
- Inherits from `SearchEngine` base class
- Returns standard result format: `{title, url, description}`
- Compatible with existing pysearx patterns
- Can be used standalone or integrated

## Future Enhancements

Potential improvements:
- [ ] Instance health monitoring
- [ ] Automatic failover
- [ ] Request caching
- [ ] Async/await support
- [ ] More category support
- [ ] Image/video search

## Files Modified

- `pysearx/engines/__init__.py` - Added SearxngEngine export
- `README.md` - Updated feature list and engine count

## Files Created

1. `pysearx/engines/searxng.py` (181 lines)
2. `utils/__init__.py` (1 line)
3. `utils/get_searxng_instances.py` (143 lines)
4. `utils/README.md` (34 lines)
5. `docs/SEARXNG.md` (283 lines)
6. `example_searxng.py` (159 lines)
7. `test_searxng.py` (136 lines)

**Total**: 7 new files, 937 lines of code and documentation

## References

- [SearXNG Project](https://github.com/searxng/searxng)
- [SearXNG Documentation](https://docs.searxng.org/)
- [searx.space](https://searx.space/) - Public instance directory
- [SearXNG Search API](https://docs.searxng.org/dev/search_api.html)
