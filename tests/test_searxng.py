"""
Test script for the SearXNG engine.
"""

from pysearx.engines.searxng import SearxngEngine
from utils.get_searxng_instances import get_best_instance


def test_searxng_default():
    """Test SearXNG engine with default instance."""
    print("Testing SearXNG with default instance...")
    engine = SearxngEngine()
    print(f"Using instance: {engine.instance_url}\n")
    
    query = "python programming"
    print(f"Searching for: '{query}'")
    
    try:
        results = engine.search(query, num_results=5)
        print(f"\nFound {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Description: {result['description'][:100]}..." if len(result['description']) > 100 else f"   Description: {result['description']}")
            print()
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_searxng_best_instance():
    """Test SearXNG engine with the best available instance."""
    print("\nTesting SearXNG with best available instance...")
    
    try:
        best_instance = get_best_instance()
        if not best_instance:
            print("No working instances found")
            return False
        
        engine = SearxngEngine(instance_url=best_instance)
        print(f"Using instance: {engine.instance_url}\n")
        
        query = "climate change"
        print(f"Searching for: '{query}'")
        
        results = engine.search(query, num_results=5)
        print(f"\nFound {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Description: {result['description'][:100]}..." if len(result['description']) > 100 else f"   Description: {result['description']}")
            print()
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_searxng_with_options():
    """Test SearXNG engine with various options."""
    print("\nTesting SearXNG with custom options...")
    
    try:
        best_instance = get_best_instance()
        engine = SearxngEngine(instance_url=best_instance)
        print(f"Using instance: {engine.instance_url}\n")
        
        query = "open source software"
        print(f"Searching for: '{query}' with safesearch=1")
        
        results = engine.search(query, num_results=3, safesearch=1)
        print(f"\nFound {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print()
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == '__main__':
    print("=" * 80)
    print("SearXNG Engine Test Suite")
    print("=" * 80 + "\n")
    
    success = True
    
    # Test with default instance
    if not test_searxng_default():
        success = False
    
    # Test with best instance
    if not test_searxng_best_instance():
        success = False
    
    # Test with options
    if not test_searxng_with_options():
        success = False
    
    print("\n" + "=" * 80)
    if success:
        print("All tests completed successfully!")
    else:
        print("Some tests failed!")
    print("=" * 80)
