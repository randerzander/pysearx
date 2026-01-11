# SearX Engine Update - Instance Rotation

## Changes Made

The SearX engine (`pysearx/engines/searx.py`) has been updated with automatic instance rotation and failure handling.

## New Features

### 1. Automatic Instance Loading
- On first use, fetches list of public SearXNG instances from searx.space
- Loads 68+ working instances (>90% uptime, HTTPS-only)
- Falls back to default instance if fetch fails

### 2. Instance Rotation
- Each search call automatically increments through the instance list
- Thread-safe rotation using locks
- Distributes load across multiple instances

### 3. Automatic Failure Handling  
- Removes instances that return 403/429/401 errors
- Maintains list of working instances
- Retries up to 3 times with different instances per query

### 4. JSON API Support
- Uses SearXNG JSON API by default (more reliable)
- Falls back to HTML parsing if needed
- Configurable via `format` parameter

## Implementation Details

### Class-Level Instance Pool
```python
class SearxEngine(SearchEngine):
    # Shared across all SearxEngine instances
    _instances: Optional[List[str]] = None  # Instance URLs
    _current_index: int = 0                  # Current rotation position
    _instances_lock = None                   # Thread safety
```

### Key Methods

**`_load_instances()`**
- Fetches instances from searx.space using utility script
- Filters by: >90% uptime, HTTPS, excludes some cloudflare
- Returns 68+ working instances

**`_get_next_instance()`**
- Returns next instance URL from rotation
- Increments index circularly
- Thread-safe with locking

**`_remove_failed_instance()`**
- Removes instance from pool when it fails
- Adjusts rotation index if needed
- Logs removal for debugging

**`search()`**
- Tries up to 3 different instances
- Removes instances on client errors (403, 429, 401)
- Returns results from first successful instance

## Test Results

### Standalone Test (`test_searx_rotation.py`)

Tested with 10 performance test queries:

```
Started with:       68 instances  
Successful queries: 2/10 (20%)
Removed instances:  15 (failed with 403 errors)
Remaining:          53 instances

Working instances identified:
- https://search.wdpserver.com
- https://searxng.cups.moe
- https://search.url4irl.com
- https://search.mdosch.de
```

**Key Observations:**
- ✅ Rotation working correctly
- ✅ Failed instances automatically removed
- ✅ Working instances successfully identified
- ⚠️ Low success rate due to aggressive rate limiting by public instances
- ✅ 2 successful queries returned 26 total results (avg 13 per query)

## Usage

### Basic Usage
```python
from pysearx.engines.searx import SearxEngine

# Initialize (loads instances automatically)
engine = SearxEngine()

# Search (automatically rotates instances)
results = engine.search("python programming")

# Each call uses the next instance in rotation
results2 = engine.search("machine learning")  # Different instance
results3 = engine.search("data science")      # Different instance
```

### With Options
```python
# Limit results
results = engine.search("query", num_results=10)

# Use HTML parsing instead of JSON
results = engine.search("query", format='html')

# Custom retry limit
results = engine.search("query", max_retries=5)
```

### Check Instance Status
```python
# See remaining instances
print(f"Instances: {len(SearxEngine._instances)}")

# See current rotation position
print(f"Index: {SearxEngine._current_index}")
```

## Advantages

1. **No Single Point of Failure** - Uses 68+ instances
2. **Automatic Failover** - Bad instances removed automatically
3. **Load Distribution** - Spreads requests across instances
4. **Self-Healing** - Adapts to instance availability
5. **Thread-Safe** - Works in parallel mode
6. **Zero Configuration** - Works out of the box

## Limitations

1. **Rate Limiting** - Public instances heavily rate limit
2. **Variable Quality** - Some instances slower than others
3. **Network Overhead** - Instance discovery takes time on first init
4. **Success Rate** - May be low due to 403 errors from instances

## Recommendations

1. **Use in Parallel Mode** - Leverage multiple engines
2. **Add Delays** - Space out searches to avoid rate limits
3. **Self-Host** - For production, run your own SearXNG instance
4. **Monitor Success** - Check which instances work best for your use case

## Files Modified

- `pysearx/engines/searx.py` - Complete rewrite with rotation

## Files Created

- `test_searx_rotation.py` - Standalone test script

## Future Enhancements

- [ ] Cache working instances to avoid re-testing
- [ ] Prefer faster instances (sort by response time)
- [ ] Exponential backoff on failures
- [ ] Instance health monitoring
- [ ] Persistent instance blacklist
