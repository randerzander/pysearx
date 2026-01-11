# Utilities

This directory contains utility scripts for pysearx.

## get_searxng_instances.py

Fetches and lists public SearXNG instances from searx.space.

### Usage

Command line:
```bash
python utils/get_searxng_instances.py
```

As a module:
```python
from utils.get_searxng_instances import get_best_instance, get_working_instances

# Get the best instance
best = get_best_instance()

# Get filtered list
instances = get_working_instances(
    min_success_rate=90.0,
    require_https=True,
    exclude_cloudflare=True
)
```

### Functions

- `fetch_instances()` - Fetch raw data from searx.space API
- `get_working_instances()` - Get filtered list of working instances
- `get_best_instance()` - Get the single best instance URL

See [../docs/SEARXNG.md](../docs/SEARXNG.md) for more details.
