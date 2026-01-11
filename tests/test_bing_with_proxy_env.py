"""
Test Bing search with proxy rotation from PROXY_FILE env var.
"""

import os
import sys

# Set the proxy file environment variable
os.environ['PROXY_FILE'] = 'working_proxies.txt'

from pysearx.engines.bing import BingEngine


def test_bing_with_proxies():
    """Test Bing search using proxy rotation."""
    print("=" * 70)
    print("TESTING BING WITH PROXY ROTATION")
    print("=" * 70)
    
    print(f"\nPROXY_FILE={os.environ.get('PROXY_FILE')}")
    print()
    
    engine = BingEngine()
    
    # Test queries
    queries = [
        "python programming",
        "machine learning", 
        "web development",
        "data science",
        "artificial intelligence"
    ]
    
    print(f"Testing {len(queries)} queries with proxy rotation...\n")
    
    successful = 0
    failed = 0
    captcha_count = 0
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. Query: '{query}'")
        
        try:
            results = engine.search(query)
            
            if results:
                successful += 1
                print(f"   ✓ SUCCESS: {len(results)} results")
                
                # Show first result
                if results:
                    print(f"      1. {results[0]['title'][:60]}...")
                    print(f"         {results[0]['url'][:70]}...")
            else:
                failed += 1
                print(f"   ⚠️  No results returned (may be CAPTCHA)")
                captcha_count += 1
        
        except Exception as e:
            failed += 1
            error_msg = str(e)
            
            if 'captcha' in error_msg.lower() or 'robot' in error_msg.lower():
                captcha_count += 1
                print(f"   ✗ CAPTCHA detected")
            else:
                print(f"   ✗ Error: {error_msg[:80]}...")
        
        print()
    
    # Summary
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\nTotal queries: {len(queries)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"CAPTCHA count: {captcha_count}")
    print(f"Success rate: {successful/len(queries)*100:.1f}%")
    
    if successful > 0:
        print("\n✅ Proxies are working for Bing!")
    else:
        print("\n⚠️  All proxies got CAPTCHA - Bing may be blocking proxy IPs")
    
    return successful > 0


if __name__ == '__main__':
    success = test_bing_with_proxies()
    sys.exit(0 if success else 1)
