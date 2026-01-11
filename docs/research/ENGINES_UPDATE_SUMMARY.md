# Search Engines Update Summary

## Overview

All search engines in pysearx have been updated with automatic rate limit handling. Engines now manage their own backoff state internally when encountering 429 (Too Many Requests) errors.

## Updates Completed

### 1. SearX Engine - Instance Rotation
**File:** `pysearx/engines/searx.py`

**Features:**
- Automatically loads 68+ public SearXNG instances from searx.space
- Rotates through instances on each search call
- Removes failed instances (403/429/401 errors)
- Retries up to 3 times with different instances
- Thread-safe instance rotation

**Test:** `test_searx_rotation.py`

### 2. All Engines - Rate Limit Backoff
**Files:** 14 engine files updated

**Features:**
- Detects 429 errors automatically
- 60-second backoff after rate limit
- Blocks requests during backoff period
- Clear countdown messages
- Independent per-engine state
- Transparent to callers

**Engines Updated:**
- Brave, DuckDuckGo, Google, Bing
- Startpage, Qwant, Mojeek, Yahoo
- Yep, Swisscows, MetaGer, Search360, Yandex

**Test:** `test_rate_limit.py`

## Implementation Details

### RateLimitMixin
Added to `pysearx/base.py`:

```python
class RateLimitMixin:
    def _check_rate_limit(self):
        """Raises exception if currently rate limited"""
        
    def _handle_rate_limit(self):
        """Sets backoff timer for 60 seconds"""
        
    def _is_rate_limit_error(self, error_str: str) -> bool:
        """Detects rate limit errors"""
```

### Engine Integration
All engines now:
1. Inherit from `RateLimitMixin` and `SearchEngine`
2. Call `_check_rate_limit()` at start of `search()`
3. Call `_handle_rate_limit()` when catching 429 errors

## Usage Examples

### SearX with Instance Rotation

```python
from pysearx.engines.searx import SearxEngine

# Automatically loads 68+ instances
engine = SearxEngine()

# Each search uses next instance
results1 = engine.search("python")      # Instance #0
results2 = engine.search("javascript")  # Instance #1
results3 = engine.search("rust")        # Instance #2

# Failed instances automatically removed
```

### Rate Limit Backoff

```python
from pysearx.engines.brave import BraveEngine

engine = BraveEngine()

try:
    results = engine.search("query")
except Exception as e:
    if "Rate limited" in str(e):
        # Engine disabled for 60 seconds
        print(e)  # "Rate limited. Try again in 58 seconds."
```

## Test Results

### SearX Instance Rotation Test
```
Started with:     68 instances
Successful:       2/10 queries (20%)
Removed:          15 failed instances
Remaining:        53 instances

Working instances identified:
- https://search.wdpserver.com
- https://searxng.cups.moe
- https://search.url4irl.com
- https://search.mdosch.de
```

**Result:** ✅ Rotation working, automatically removes failed instances

### Rate Limit Backoff Test
```
✓ Rate limit error detection
✓ Backoff timer sets correctly
✓ Requests blocked during backoff
✓ Engine recovers after 60 seconds
✓ Independent limits per engine
✓ Clear error messages
```

**Result:** ✅ All core functionality working

## Benefits

1. **SearX Improvements:**
   - No single point of failure (68+ instances)
   - Automatic failover
   - Load distribution
   - Self-healing instance pool

2. **Rate Limit Improvements:**
   - Prevents wasted requests during backoff
   - Clear user feedback
   - Automatic recovery
   - No API changes needed

## Files Created

- `test_searx_rotation.py` - SearX rotation test
- `test_rate_limit.py` - Rate limit backoff test
- `update_engines_rate_limit.py` - Update automation script
- `SEARX_ROTATION_UPDATE.md` - SearX rotation documentation
- `RATE_LIMIT_BACKOFF.md` - Rate limit documentation
- `ENGINES_UPDATE_SUMMARY.md` - This file

## Files Modified

- `pysearx/base.py` - Added RateLimitMixin
- `pysearx/engines/searx.py` - Complete rewrite with rotation
- 14 engine files - Added rate limit backoff

## Recommendations

1. **For Production:**
   - Consider self-hosting SearXNG instance
   - Add delays between searches
   - Monitor which engines get rate limited

2. **For Development:**
   - Use parallel mode to leverage multiple engines
   - Handle rate limit exceptions gracefully
   - Log rate limit events for monitoring

## Future Enhancements

- [ ] Exponential backoff on repeated rate limits
- [ ] Respect `Retry-After` header
- [ ] Instance health monitoring
- [ ] Persistent instance blacklist
- [ ] Metrics/logging for rate limit events
- [ ] Configurable backoff duration per engine
