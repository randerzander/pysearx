# Quick Start: Using API-Based Search Engines

This guide helps you get started with the new API-based search engines that avoid CAPTCHA and blocking issues.

## TL;DR

**Problem**: HTML scraping can encounter CAPTCHA challenges and bot blocking.

**Solution**: Use official API packages instead.

**Best Option**: DuckDuckGo API (`ddgs` package) - Free, no API key, no CAPTCHA.

**NEW**: DuckDuckGo API is now the **DEFAULT** - just install `ddgs` and use `search()` normally!

## Installation

### Option 1: DuckDuckGo API (Recommended) ✅ **NOW DEFAULT**

```bash
pip install pysearx[ddg-api]
```

Or just the package:
```bash
pip install ddgs
```

**That's it!** The DuckDuckGo API engine is now used automatically by default when you call `search()`.

### Option 2: Bing API (Optional, requires API key)

```bash
pip install pysearx[bing-api]
```

### Option 3: Install both

```bash
pip install pysearx[all-apis]
```

## Usage Examples

### DuckDuckGo API (Now Default!) ✅

**Simple usage** (DuckDuckGo API used automatically):

```python
from pysearx import search

# That's it! Uses DuckDuckGo API automatically if ddgs is installed
results = search("python programming", max_results=10)

for result in results:
    print(f"{result['title']}: {result['url']}")
```

**Explicit usage** (same as above):

```python
from pysearx import search
from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine

# Create engine (not needed - it's already the default!)
ddg_api = DuckDuckGoAPIEngine()

# Search
results = search("python programming", engines=[ddg_api], max_results=10)

for result in results:
    print(f"{result['title']}: {result['url']}")
```

**Automatic Fallback:**

If `ddgs` is not installed, pysearx automatically falls back to HTML scraping for DuckDuckGo:

```python
# Without ddgs installed:
# - Uses DuckDuckGoEngine (HTML scraping)
# - May encounter CAPTCHA/blocking

# With ddgs installed:
# - Uses DuckDuckGoAPIEngine (API)
# - No CAPTCHA/blocking issues
```

**Benefits:**
- ✅ Free (no API key)
- ✅ No CAPTCHA
- ✅ No blocking
- ✅ More reliable than HTML scraping
- ✅ **Used by default** - no code changes needed!

### Bing API (Optional)

```python
from pysearx import search
from pysearx.engines.bing_api import BingAPIEngine

# Requires API key from Azure Portal
api_key = "YOUR_BING_API_KEY"
bing_api = BingAPIEngine(api_key=api_key)

# Search
results = search("web development", engines=[bing_api], max_results=10)
```

**Getting a Bing API Key:**
1. Sign up for Azure: https://azure.microsoft.com/
2. Create a Bing Search resource
3. Copy your API key from Azure Portal

**Pricing:**
- Free tier: 1,000 requests/month
- Paid: $3 per 1,000 requests

## Comparison

| Feature | DuckDuckGo API | Bing API | HTML Scraping |
|---------|---------------|----------|---------------|
| Cost | Free | Free tier limited | Free |
| API Key | ❌ No | ✅ Yes | ❌ No |
| CAPTCHA | ❌ No | ❌ No | ✅ Yes |
| Blocking | ❌ No | ❌ No | ✅ Yes |
| Reliability | High | Very High | Medium |

## Recommendation

1. **Use DuckDuckGo API** for best results without cost
2. **Use Bing API** if you have Azure subscription and need guaranteed reliability
3. **HTML engines** work as fallback when APIs are unavailable

## Mixed Usage

You can combine API and HTML engines:

```python
from pysearx import search
from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine
from pysearx.engines.google import GoogleEngine
from pysearx.engines.brave import BraveEngine

engines = [
    DuckDuckGoAPIEngine(),  # API - most reliable
    GoogleEngine(),          # HTML fallback
    BraveEngine(),          # HTML fallback
]

results = search("python", engines=engines, max_results=10)
```

## More Information

- Full research: See `SEARCH_PACKAGES_RESEARCH.md`
- Example code: Run `python example_api_engines.py`
- Package docs: 
  - DuckDuckGo: https://pypi.org/project/ddgs/
  - Bing: https://learn.microsoft.com/en-us/azure/cognitive-services/bing-web-search/

## Troubleshooting

### ImportError: No module named 'ddgs'

Install the package:
```bash
pip install ddgs
```

### ImportError when using DuckDuckGoAPIEngine

Make sure you installed the optional dependency:
```bash
pip install pysearx[ddg-api]
```

### Bing API authentication errors

Check that:
1. Your API key is correct
2. Your Azure subscription is active
3. You haven't exceeded rate limits

## Testing

Run the tests:
```bash
python -m unittest test_api_engines
```

All tests should pass (one may be skipped if azure package is not installed).
