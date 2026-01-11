# PySearx Documentation

## 📚 Quick Links

### Getting Started
- [README.md](../README.md) - Main project documentation
- [QUICKSTART_API_ENGINES.md](QUICKSTART_API_ENGINES.md) - Quick start guide for API-based engines
- [IMPLEMENTATION.md](IMPLEMENTATION.md) - Implementation details

### Integration Guides
- [SEARXNG_INTEGRATION.md](SEARXNG_INTEGRATION.md) - How to integrate SearXNG
- [SEARXNG_QUICKSTART.md](SEARXNG_QUICKSTART.md) - SearXNG quick start
- [SEARX_ROTATION_UPDATE.md](SEARX_ROTATION_UPDATE.md) - SearX rotation implementation

### Examples
- [examples/example.py](examples/example.py) - Basic usage example
- [examples/example_api_engines.py](examples/example_api_engines.py) - API engines example
- [examples/example_searxng.py](examples/example_searxng.py) - SearXNG example
- [examples/demo.py](examples/demo.py) - Demo script

---

## 🔬 Research & Analysis

### Engine Analysis
- [analysis/DUCKDUCKGO_FINAL_ANALYSIS.md](analysis/DUCKDUCKGO_FINAL_ANALYSIS.md) - DuckDuckGo testing results
- [analysis/BRAVE_PROXY_FALLBACK_SUMMARY.md](analysis/BRAVE_PROXY_FALLBACK_SUMMARY.md) - Brave proxy implementation
- [analysis/BING_PROXY_ANALYSIS.md](analysis/BING_PROXY_ANALYSIS.md) - Bing proxy testing
- [analysis/PERFORMANCE_SUMMARY.md](analysis/PERFORMANCE_SUMMARY.md) - Performance benchmarks

### Proxy Implementation
- [analysis/PROXY_IMPLEMENTATION_SUMMARY.md](analysis/PROXY_IMPLEMENTATION_SUMMARY.md) - Proxy implementation overview
- [analysis/PROXY_TEST_FINAL_RESULTS.md](analysis/PROXY_TEST_FINAL_RESULTS.md) - Proxy testing results

### Research Documents
- [research/ENGINE_DEFAULTS_UPDATE.md](research/ENGINE_DEFAULTS_UPDATE.md) - Default engines configuration
- [research/RATE_LIMIT_BACKOFF.md](research/RATE_LIMIT_BACKOFF.md) - Rate limit & backoff implementation
- [research/ENGINES_UPDATE_SUMMARY.md](research/ENGINES_UPDATE_SUMMARY.md) - Engine updates summary
- [research/SEARCH_PACKAGES_RESEARCH.md](research/SEARCH_PACKAGES_RESEARCH.md) - Research on search packages

---

## 🎯 Default Configuration

**Enabled by default (100% reliable):**
1. DuckDuckGo (API) - ~20 results
2. Yahoo - ~10-15 results
3. Mojeek - ~10-12 results
4. Brave - Auto-enabled when `PROXY_FILE` env var is set

**Total:** 3-4 engines, ~40-70 results, 100% success rate

See [research/ENGINE_DEFAULTS_UPDATE.md](research/ENGINE_DEFAULTS_UPDATE.md) for details.

---

## 📂 Directory Structure

```
docs/
├── README.md                    # This file
├── IMPLEMENTATION.md            # Implementation guide
├── QUICKSTART_API_ENGINES.md    # Quick start
├── SEARXNG_INTEGRATION.md       # SearXNG integration
├── SEARXNG_QUICKSTART.md        # SearXNG quick start
├── SEARX_ROTATION_UPDATE.md     # SearX rotation
├── analysis/                    # Analysis documents
│   ├── BING_PROXY_ANALYSIS.md
│   ├── BRAVE_PROXY_FALLBACK_SUMMARY.md
│   ├── DUCKDUCKGO_ANALYSIS.md
│   ├── DUCKDUCKGO_FINAL_ANALYSIS.md
│   ├── PERFORMANCE_SUMMARY.md
│   ├── PROXY_IMPLEMENTATION_SUMMARY.md
│   └── PROXY_TEST_FINAL_RESULTS.md
├── examples/                    # Example scripts
│   ├── demo.py
│   ├── example.py
│   ├── example_api_engines.py
│   └── example_searxng.py
└── research/                    # Research documents
    ├── ENGINES_UPDATE_SUMMARY.md
    ├── ENGINE_DEFAULTS_UPDATE.md
    ├── RATE_LIMIT_BACKOFF.md
    └── SEARCH_PACKAGES_RESEARCH.md
```

---

## 🧪 Testing

All tests are located in `../tests/`:

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_performance.py

# Test with proxies
export PROXY_FILE=tests/proxies/working_proxies.txt
python tests/test_performance.py
```

Test data:
- `tests/proxies/` - Proxy lists (http.txt, working_proxies.txt)
- `tests/performance_results.json` - Performance benchmark results
- `tests/proxy_test_results.log` - Proxy test logs

---

## 🔧 Utilities

Located in `../utils/`:

- `get_searxng_instances.py` - Fetch public SearXNG instances
- `update_engines_rate_limit.py` - Update engine rate limits

---

## 📖 Additional Resources

- [Project README](../README.md) - Main documentation
- [Setup Guide](../setup.py) - Installation configuration
- [Tests Directory](../tests/) - All test scripts
- [Utils Directory](../utils/) - Utility scripts
