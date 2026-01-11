# Proxy Support Implementation & Testing

## Summary

✅ **Proxy support implemented** - pysearx now supports proxy rotation via `PROXY_FILE` environment variable  
⚠️ **Bing still blocks** - Free datacenter proxies get CAPTCHA from Bing  
✓ **System works** - Proxy rotation confirmed working, just need better proxies

## Implementation

### 1. Created `working_proxies.txt`
- Contains 20 working proxies from `http.txt` (out of 1,875 tested)
- Success rate: 1.1% of free proxies are still alive
- Proxies tested and verified to work for basic HTTP requests

### 2. Added ProxyManager to `pysearx/base.py`

```python
class ProxyManager:
    """Manages proxy rotation from a file."""
    
    @classmethod
    def load_proxies(cls, proxy_file: str) -> List[str]:
        """Load proxies from file."""
    
    @classmethod
    def get_next_proxy(cls) -> Optional[str]:
        """Get next proxy in rotation."""
```

### 3. Added `get_proxy_dict()` Helper Function

```python
def get_proxy_dict(proxy_url: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    Get proxy dictionary for requests library.
    Checks PROXY_FILE environment variable if proxy_url not provided.
    """
```

### 4. Updated Bing Engine

Modified `pysearx/engines/bing.py`:
```python
# Get proxy if PROXY_FILE env var is set
proxies = get_proxy_dict()

# Make the request
response = requests.get(
    self.base_url,
    params=params,
    headers=headers,
    proxies=proxies,  # <-- Proxy support added
    timeout=self.timeout
)
```

## Usage

### Set environment variable:
```bash
export PROXY_FILE=working_proxies.txt
```

### Use normally:
```python
from pysearx.engines.bing import BingEngine

engine = BingEngine()
results = engine.search("python programming")
# Automatically uses proxies from PROXY_FILE
```

### Proxy rotation:
- First search uses proxy #1
- Second search uses proxy #2
- Third search uses proxy #3
- After last proxy, cycles back to #1

## Test Results

### Proxy Discovery Test (`test_proxies_fast.py`)
```
Total proxies tested: 1,875
Working proxies found: 20
Success rate: 1.1%
Test time: 57.8 seconds
```

**Working proxies saved to `working_proxies.txt`**

### Proxy Rotation Test
```bash
$ python test_bing_with_proxy_env.py
```

**Results:**
- ✅ Proxy system working correctly
- ✅ Rotating through 20 proxies
- ❌ All 5 queries returned CAPTCHA
- ❌ 0% success rate with Bing

**Conclusion:** Free datacenter proxies are detected and blocked by Bing.

## Why Free Proxies Don't Work with Bing

1. **Datacenter IPs** - Free proxies are typically from datacenters, not residential
2. **Known ranges** - Bing maintains blacklists of common proxy IP ranges
3. **Shared IPs** - Many users abuse the same free proxies
4. **Behavioral patterns** - Datacenter traffic patterns differ from residential

## What Would Work

### Option 1: Residential Proxies (Paid) 💰
- **Cost:** $10-50/month
- **Success:** High (90%+)
- **Services:** Bright Data, Oxylabs, Smartproxy
- Proxies from real residential IPs
- Bing treats them like normal users

### Option 2: Bing API (Free Tier Available) ✅
- **Cost:** Free tier (1,000 calls/month), then $3-7/1000
- **Success:** 100%
- **Already implemented:** `pysearx/engines/bing_api.py`
- Official, no blocking, reliable

### Option 3: Accept Limitation 📝
- Document that Bing scraping requires proxies or API
- Keep Bing disabled by default
- Rely on working engines (Mojeek, Yahoo)

## Files Created

- `working_proxies.txt` - 20 verified working proxies
- `test_proxies_fast.py` - Parallel proxy testing script
- `test_all_proxies.py` - Sequential proxy testing script
- `test_bing_with_proxy_env.py` - Test Bing with proxy rotation

## Files Modified

- `pysearx/base.py` - Added ProxyManager and get_proxy_dict()
- `pysearx/engines/bing.py` - Added proxy support

## Next Steps

### To use with working proxies:
1. **Get residential proxies** (paid service)
2. **Add to `working_proxies.txt`**
3. **Set `export PROXY_FILE=working_proxies.txt`**
4. **Run searches** - will automatically use proxies

### To extend proxy support to all engines:
Similar changes can be made to other engines:
- Import `get_proxy_dict` from base
- Add `proxies=get_proxy_dict()` to requests.get() calls

## Verification

✅ Proxy loading works  
✅ Proxy rotation works  
✅ Proxies are used in requests  
✅ 20 working proxies identified  
❌ Bing blocks free proxy IPs  
✅ System ready for premium proxies

## Recommendation

**For Production:**
1. Use **Bing API** (already implemented, free tier available)
2. Or buy **residential proxy service** (~$20/month)
3. Current free proxies good for **testing only**

**For Development:**
- Rely on **Mojeek** and **Yahoo** (work without proxies)
- Use **SearX** with instance rotation (20% success)
- Test proxy system with `working_proxies.txt` (confirmed working)
