"""
Example script demonstrating how to use the SearXNG engine with pysearx.

This script shows:
1. Using the default SearXNG instance
2. Using a custom instance from searx.space
3. Various search options
"""

from pysearx.engines.searxng import SearxngEngine
from utils.get_searxng_instances import get_best_instance, get_working_instances


def example_default_instance():
    """Example 1: Using the default SearXNG instance."""
    print("Example 1: Using default SearXNG instance")
    print("-" * 50)
    
    # Create engine with default instance
    engine = SearxngEngine()
    
    # Perform a search
    results = engine.search("python tutorials", num_results=5)
    
    print(f"Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}")
        if result['description']:
            print(f"   {result['description'][:100]}...")
        print()


def example_custom_instance():
    """Example 2: Using a custom SearXNG instance from searx.space."""
    print("\nExample 2: Using custom SearXNG instance")
    print("-" * 50)
    
    # Get the best available instance
    instance_url = get_best_instance()
    print(f"Using instance: {instance_url}\n")
    
    # Create engine with custom instance
    engine = SearxngEngine(instance_url=instance_url)
    
    # Perform a search
    results = engine.search("climate change", num_results=5)
    
    print(f"Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}")
        print()


def example_with_options():
    """Example 3: Using search options."""
    print("\nExample 3: Using search options")
    print("-" * 50)
    
    instance_url = get_best_instance()
    engine = SearxngEngine(instance_url=instance_url)
    
    # Search with safe search enabled
    results = engine.search(
        "artificial intelligence",
        num_results=3,
        safesearch=1,  # Moderate safe search
        language='en'
    )
    
    print(f"Found {len(results)} results with safesearch:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}")
        print()


def example_list_instances():
    """Example 4: List available SearXNG instances."""
    print("\nExample 4: List available SearXNG instances")
    print("-" * 50)
    
    instances = get_working_instances(min_success_rate=90.0)
    
    print(f"Top 10 SearXNG instances:\n")
    for i, instance in enumerate(instances[:10], 1):
        print(f"{i}. {instance['url']}")
        print(f"   Success: {instance['success_percentage']:.1f}% | "
              f"Response: {instance['response_time']:.3f}s | "
              f"TLS: {instance['tls_grade']}")
        print()


def example_fallback_instances():
    """Example 5: Using fallback instances if primary fails."""
    print("\nExample 5: Using fallback instances")
    print("-" * 50)
    
    # Get top 3 instances as fallbacks
    instances = get_working_instances()[:3]
    query = "open source software"
    
    for instance in instances:
        try:
            engine = SearxngEngine(instance_url=instance['url'])
            results = engine.search(query, num_results=3)
            
            print(f"Successfully searched using: {instance['url']}")
            print(f"Found {len(results)} results\n")
            
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
            
            break  # Success, exit loop
            
        except Exception as e:
            print(f"Failed with {instance['url']}: {e}")
            print("Trying next instance...\n")
            continue


if __name__ == '__main__':
    print("=" * 60)
    print("SearXNG Engine Examples for pysearx")
    print("=" * 60 + "\n")
    
    try:
        # Run examples (commented out the ones that might fail due to rate limiting)
        # example_default_instance()
        # example_custom_instance()
        # example_with_options()
        example_list_instances()
        # example_fallback_instances()
        
        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
