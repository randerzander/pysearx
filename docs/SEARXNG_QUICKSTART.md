# SearXNG Quick Start

## Installation

Already included in pysearx! No additional dependencies needed.

## Basic Usage

```python
from pysearx.engines.searxng import SearxngEngine

# Create engine
engine = SearxngEngine()

# Search
results = engine.search("your query here")

# Display results
for result in results:
    print(f"{result['title']}")
    print(f"{result['url']}")
    print(f"{result['description']}\n")
```

## Using Best Instance

```python
from pysearx.engines.searxng import SearxngEngine
from utils.get_searxng_instances import get_best_instance

# Get best performing instance
instance_url = get_best_instance()

# Create engine with best instance
engine = SearxngEngine(instance_url=instance_url)

# Search
results = engine.search("your query", num_results=10)
```

## List Available Instances

```bash
python utils/get_searxng_instances.py
```

## Search Options

```python
results = engine.search(
    "your query",
    num_results=10,      # Limit results
    language='en',       # Language code
    safesearch=1,        # 0=off, 1=moderate, 2=strict
    category='general'   # general, images, videos, news, etc.
)
```

## Common Patterns

### Fallback to Multiple Instances

```python
from utils.get_searxng_instances import get_working_instances

instances = get_working_instances()[:3]  # Top 3

for instance in instances:
    try:
        engine = SearxngEngine(instance_url=instance['url'])
        results = engine.search("query")
        break  # Success
    except:
        continue  # Try next
```

### Custom Instance

```python
# Use your own or specific instance
engine = SearxngEngine(instance_url="https://searx.tiekoetter.com")
results = engine.search("query")
```

## Result Format

```python
{
    'title': str,        # Page title
    'url': str,          # Page URL  
    'description': str   # Snippet/summary
}
```

## More Information

- Full documentation: `docs/SEARXNG.md`
- Examples: `example_searxng.py`
- Implementation details: `SEARXNG_INTEGRATION.md`
