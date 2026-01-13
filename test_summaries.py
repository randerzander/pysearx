from pysearx.search import search, DEFAULT_ENGINES
import os

# Test with a simple query
query = "python programming"
print(f"Searching for: {query}")

# Use default engines (DuckDuckGo API, Yahoo, Mojeek)
results = search(query, max_results=5)

for i, res in enumerate(results, 1):
    print(f"\nResult {i}:")
    print(f"  Title: {res['title']}")
    print(f"  URL: {res['url']}")
    print(f"  Engine: {res['engine']}")
    print(f"  Description: {res.get('description', 'MISSING')[:100]}...")
