# Exponential Backoff Persistence Fix

## Problem

The exponential backoff mechanism was not working correctly across multiple search queries. When a search engine (like Mojeek) was rate-limited or blocked with a 403 error:

1. Query 1: Gets 403 → Backs off for 1s (Attempt #1)
2. Query 2: Waits 1s → Gets 403 → Backs off for 1s (Attempt #1) ❌
3. Query 3: Waits 1s → Gets 403 → Backs off for 1s (Attempt #1) ❌

**Expected behavior**: Backoff should increase exponentially (1s → 2s → 4s → 8s...) to avoid hammering rate-limited services.

**Root cause**: The rate limit counter was being reset when the backoff timer expired, even though no successful request had been made.

## Solution

Modified `RateLimitMixin` in `pysearx/base.py`:

1. **Don't reset counter on expiry**: When the backoff timer expires, we now only clear the timer but preserve the count. The counter only resets after a successful request.

2. **Added `_reset_rate_limit()` method**: Engines now explicitly call this method when a request succeeds, which resets both the timer and the counter.

3. **Updated all engines**: Added `_reset_rate_limit()` calls to all engines using `RateLimitMixin`:
   - `mojeek.py`
   - `brave.py`
   - `yahoo.py`
   - `duckduckgo.py`
   - `bing.py`
   - `qwant.py`

## Per-Engine Isolation

**Important**: Each engine instance maintains its own independent backoff state. This means:

- If Mojeek gets rate-limited, Yahoo and DuckDuckGo continue working normally
- Each engine has its own `_rate_limit_count` and `_rate_limited_until` timer
- `DEFAULT_ENGINES` contains singleton instances (created once at module import)
- State persists across all `search()` calls using the same engine instance

Example:
```python
from pysearx import search

# First search - Mojeek gets 403
search("query 1")  # Mojeek: Attempt #1, backs off 1s; Yahoo: works fine

# Second search - Mojeek still blocked
search("query 2")  # Mojeek: Attempt #2, backs off 2s; Yahoo: works fine

# Third search - Mojeek still blocked  
search("query 3")  # Mojeek: Attempt #3, backs off 4s; Yahoo: works fine
```

## Changes Made

### `pysearx/base.py`

1. Modified `_check_rate_limit()` to not reset the counter when backoff expires
2. Added `_reset_rate_limit()` method to reset state after successful requests

### Engine files

Added `self._reset_rate_limit()` before returning results in all engines using rate limiting.

### Tests

1. Updated `tests/test_exponential_backoff.py` to verify the new behavior
2. Created `test_persistent_backoff.py` to demonstrate persistence across queries
3. Created `test_per_engine_backoff.py` to verify per-engine isolation

## Verification

Run the tests:

```bash
# Test exponential backoff progression
python3 tests/test_exponential_backoff.py

# Test persistence across queries
python3 test_persistent_backoff.py

# Test per-engine isolation
python3 test_per_engine_backoff.py
```

All tests should pass, showing:
- ✅ Backoff persists across failed queries
- ✅ Backoff resets only after successful requests
- ✅ Backoff is independent per engine
- ✅ Exponential progression works correctly (1s, 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 300s max)

## Impact

Now when a search engine is rate-limited or blocked:

- Query 1: Gets 403 → Backs off for 1s (Attempt #1)
- Query 2: Gets 403 → Backs off for 2s (Attempt #2) ✅
- Query 3: Gets 403 → Backs off for 4s (Attempt #3) ✅
- Query 4: Gets 403 → Backs off for 8s (Attempt #4) ✅
- ...continues until max 300s (5 minutes)

This dramatically reduces wasted requests to rate-limited services and avoids further blocking/penalties, while allowing other engines to continue working normally.
