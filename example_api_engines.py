"""
Example usage of API-based search engines.

This example demonstrates how to use the new API-based engines
for DuckDuckGo and Bing, which avoid CAPTCHA and blocking issues.
"""

from pysearx import search


def example_duckduckgo_api():
    """Example using DuckDuckGo API engine (recommended)."""
    print("=" * 70)
    print("DuckDuckGo API Engine Example")
    print("=" * 70)
    
    try:
        from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine, is_available
        
        if not is_available():
            print("⚠️  DuckDuckGo API engine not available")
            print("   Install with: pip install pysearx[ddg-api]")
            print("   Or: pip install ddgs")
            return
        
        print("✓ DuckDuckGo API engine available")
        print("\nSearching for 'python programming'...")
        
        # Create the API engine
        ddg_api = DuckDuckGoAPIEngine()
        
        # Use it with the search function
        results = search("python programming", engines=[ddg_api], max_results=5)
        
        print(f"\n✓ Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Description: {result.get('description', 'No description')[:100]}...")
            print(f"   Engine: {result['engine']}")
            print()
        
        print("Benefits:")
        print("  ✓ No CAPTCHA challenges")
        print("  ✓ No bot detection/blocking")
        print("  ✓ More reliable than HTML scraping")
        print("  ✓ Free to use, no API key required")
        
    except ImportError as e:
        print(f"⚠️  Could not import DuckDuckGo API engine: {e}")
        print("   Install with: pip install pysearx[ddg-api]")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_bing_api():
    """Example using Bing API engine (requires API key)."""
    print("\n" + "=" * 70)
    print("Bing API Engine Example")
    print("=" * 70)
    
    try:
        from pysearx.engines.bing_api import BingAPIEngine, is_available
        
        if not is_available():
            print("⚠️  Bing API engine not available")
            print("   Install with: pip install pysearx[bing-api]")
            print("   Or: pip install azure-cognitiveservices-search-websearch")
            return
        
        print("✓ Bing API package available")
        print("\n⚠️  Note: Bing API requires an API key from Azure Portal")
        print("   Get your key from: https://portal.azure.com/")
        print("   Free tier: 1,000 transactions per month")
        
        # Example (requires actual API key to run)
        print("\nExample code:")
        print("""
    # Get your API key from Azure Portal
    api_key = "YOUR_BING_API_KEY"
    
    # Create Bing API engine
    bing_api = BingAPIEngine(api_key=api_key)
    
    # Use it with search
    results = search("python programming", engines=[bing_api], max_results=5)
    
    for result in results:
        print(f"{result['title']}: {result['url']}")
        """)
        
        print("\nBenefits:")
        print("  ✓ Official Microsoft API")
        print("  ✓ 100% reliable, no blocking")
        print("  ✓ Rich metadata")
        print("  ✗ Requires API key")
        print("  ✗ Paid service (free tier limited)")
        
    except ImportError as e:
        print(f"⚠️  Could not import Bing API engine: {e}")
        print("   Install with: pip install pysearx[bing-api]")


def example_comparison():
    """Compare different engine types."""
    print("\n" + "=" * 70)
    print("Engine Comparison")
    print("=" * 70)
    
    print("\n1. HTML Scraping Engines (default)")
    print("   - DuckDuckGoEngine, BingEngine, GoogleEngine, etc.")
    print("   - Pros: Free, no setup required")
    print("   - Cons: May encounter CAPTCHA or blocking")
    print("   - Use case: General purpose, fallback")
    
    print("\n2. DuckDuckGo API Engine (recommended)")
    print("   - DuckDuckGoAPIEngine (uses 'ddgs' package)")
    print("   - Pros: Free, no CAPTCHA, reliable")
    print("   - Cons: Requires 'ddgs' package")
    print("   - Use case: Primary DuckDuckGo searches")
    
    print("\n3. Bing API Engine (optional)")
    print("   - BingAPIEngine (uses Azure API)")
    print("   - Pros: Very reliable, official API")
    print("   - Cons: Requires API key, paid (limited free tier)")
    print("   - Use case: Enterprise, guaranteed reliability")
    
    print("\nRecommendation:")
    print("  → Use DuckDuckGoAPIEngine for best results without cost")
    print("  → Use BingAPIEngine if you have Azure subscription")
    print("  → HTML engines as fallback when APIs unavailable")


def example_mixed_engines():
    """Example using both API and HTML scraping engines."""
    print("\n" + "=" * 70)
    print("Mixed Engines Example")
    print("=" * 70)
    
    print("\nCombining API-based and HTML scraping engines...")
    
    engines = []
    
    # Try to add DuckDuckGo API engine
    try:
        from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine, is_available
        if is_available():
            engines.append(DuckDuckGoAPIEngine())
            print("✓ Added DuckDuckGo API engine")
    except ImportError:
        print("⚠️  DuckDuckGo API not available, skipping")
    
    # Add some HTML scraping engines as fallback
    from pysearx.engines.google import GoogleEngine
    from pysearx.engines.brave import BraveEngine
    
    engines.extend([GoogleEngine(), BraveEngine()])
    print("✓ Added Google and Brave HTML engines")
    
    if engines:
        print(f"\nTotal engines: {len(engines)}")
        print("\nExample search (not executed in this demo):")
        print(f"  results = search('python', engines={[e.name for e in engines]}, max_results=10)")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "API-Based Search Engines Examples" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")
    
    example_duckduckgo_api()
    example_bing_api()
    example_comparison()
    example_mixed_engines()
    
    print("\n" + "=" * 70)
    print("For more information, see SEARCH_PACKAGES_RESEARCH.md")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
