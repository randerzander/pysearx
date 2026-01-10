"""
Example usage of pysearx library.

This example demonstrates how to use the pysearx library to search
the web and retrieve results.
"""

from pysearx import search

def main():
    # Basic search
    print("Searching for 'python programming'...")
    results = search("python programming", max_results=5)
    
    print(f"\nFound {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Description: {result.get('description', 'No description available')}")
        print(f"   Engine: {result['engine']}")
        print()

if __name__ == '__main__':
    main()
