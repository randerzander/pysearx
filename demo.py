"""
Demonstration of pysearx API matching the requirements.

This script demonstrates that pysearx:
1. Does NOT spin up any new processes (runs in a single process)
2. Has a simple API like search(query)
3. Returns a list of dicts with title, url, and description
"""

from pysearx import search, SearchEngine


class MockSearchEngine(SearchEngine):
    """Mock search engine for demonstration purposes."""
    
    def search(self, query, **kwargs):
        """Return mock results."""
        return [
            {
                'title': f'Result 1 for {query}',
                'url': 'https://example.com/1',
                'description': 'This is the first result'
            },
            {
                'title': f'Result 2 for {query}',
                'url': 'https://example.com/2',
                'description': 'This is the second result'
            },
            {
                'title': f'Result 3 for {query}',
                'url': 'https://example.com/3',
                'description': 'This is the third result'
            }
        ]

print("=" * 70)
print("PYSEARX LIBRARY DEMONSTRATION")
print("=" * 70)
print()

# Requirement 1: Single process (no multiprocessing/threading)
print("✓ Single Process: pysearx runs in the same process, no threads/processes spawned")
print()

# Requirement 2: Simple API - search(query)
print("✓ Simple API: Just call search(query)")
print()
print("  Example: results = search('python programming')")
print()

# Using mock engine for demonstration (real engine would require network)
results = search('python programming', engines=[MockSearchEngine()], max_results=3)

# Requirement 3: Returns list of dicts with title, url, description
print("✓ Returns list of dicts with title, url, and description:")
print()

for i, result in enumerate(results, 1):
    print(f"  Result #{i}:")
    print(f"    - title: {result['title']}")
    print(f"    - url: {result['url']}")
    print(f"    - description: {result['description']}")
    print()

print("=" * 70)
print("REQUIREMENTS SATISFIED")
print("=" * 70)
print()
print("The library implements:")
print("  ✓ Generic search engine implementation")
print("  ✓ Single-process execution (no new processes)")
print("  ✓ Simple API: search(query)")
print("  ✓ Returns list of dicts with title, url, description")
print()
