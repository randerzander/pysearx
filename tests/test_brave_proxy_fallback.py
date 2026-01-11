"""
Test Brave engine with automatic proxy fallback on 429.
"""

import os
import sys

# Set proxy file
os.environ['PROXY_FILE'] = 'working_proxies.txt'

from pysearx.engines.brave import BraveEngine


def test_brave_proxy_fallback():
    """Test that Brave switches to proxies after 429."""
    print("=" * 70)
    print("TESTING BRAVE WITH AUTOMATIC PROXY FALLBACK")
    print("=" * 70)
    
    print(f"\nPROXY_FILE={os.getenv('PROXY_FILE')}")
    print("\nStrategy:")
    print("  1. Start without proxies")
    print("  2. When 429 occurs, switch to proxy mode")
    print("  3. Continue using proxies for subsequent requests")
    print()
    
    engine = BraveEngine()
    
    queries = [
        "python programming",
        "machine learning",
        "web development",
        "data science",
        "artificial intelligence",
        "cloud computing",
        "cybersecurity",
        "blockchain",
        "quantum computing",
        "neural networks"
    ]
    
    print(f"Testing {len(queries)} queries...")
    print("=" * 70)
    
    successful = 0
    failed = 0
    rate_limited = 0
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        try:
            results = engine.search(query)
            
            if results:
                successful += 1
                print(f"   ✓ SUCCESS: {len(results)} results")
                if results[0]:
                    print(f"      1. {results[0]['title'][:55]}...")
            else:
                failed += 1
                print(f"   ⚠️  No results (CAPTCHA or parsing issue)")
        
        except Exception as e:
            error_msg = str(e)
            
            if 'Rate limited' in error_msg:
                rate_limited += 1
                print(f"   ⏸️  Rate limited: {error_msg}")
                print(f"      (Will use proxy on next request)")
            elif '429' in error_msg or 'rate limit' in error_msg.lower():
                rate_limited += 1
                print(f"   ⚠️  429/Rate limit: {error_msg[:60]}...")
                print(f"      Engine should switch to proxy mode now")
            else:
                failed += 1
                print(f"   ✗ Error: {error_msg[:60]}...")
    
    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\nTotal queries: {len(queries)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Rate limited: {rate_limited}")
    print(f"Success rate: {successful/len(queries)*100:.1f}%")
    
    print(f"\nEngine state:")
    print(f"  Using proxy: {engine._use_proxy}")
    print(f"  Failed without proxy: {engine._failed_without_proxy}")
    
    if successful > 0:
        print("\n✅ Brave worked (at least partially)!")
        if engine._use_proxy:
            print("   💡 Switched to proxy mode after rate limit")
    else:
        print("\n⚠️  All queries failed")
        if engine._use_proxy:
            print("   Note: Even proxies got blocked")
        else:
            print("   Note: Never got rate limited, different issue")
    
    return successful > 0


if __name__ == '__main__':
    success = test_brave_proxy_fallback()
    sys.exit(0 if success else 1)
