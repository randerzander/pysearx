"""Test DuckDuckGo with proxy fallback after rate limiting."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set proxy file
os.environ['PROXY_FILE'] = 'working_proxies.txt'

import time
from pysearx.engines.duckduckgo import DuckDuckGoEngine


def test_duckduckgo_with_proxies():
    """Test DuckDuckGo with automatic proxy fallback."""
    print("=" * 80)
    print("DUCKDUCKGO WITH PROXY FALLBACK TEST")
    print("=" * 80)
    
    engine = DuckDuckGoEngine()
    
    queries = [
        "python programming",
        "javascript tutorial", 
        "golang best practices",
        "rust programming",
        "kotlin android",
        "swift ios",
        "typescript guide",
        "ruby rails",
        "php frameworks",
        "java spring",
    ]
    
    print(f"\nTesting {len(queries)} queries with proxy fallback enabled...")
    print(f"PROXY_FILE: {os.environ.get('PROXY_FILE')}")
    print()
    
    success_count = 0
    direct_success = 0
    proxy_success = 0
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print(f"   Use proxy: {engine._use_proxy}")
        
        try:
            results = engine.search(query)
            
            if results and len(results) > 0:
                print(f"   ✓ SUCCESS: {len(results)} results")
                print(f"      First: {results[0]['title'][:50]}...")
                success_count += 1
                
                if engine._use_proxy:
                    proxy_success += 1
                else:
                    direct_success += 1
            else:
                print(f"   ⚠️  EMPTY RESULTS")
                
        except Exception as e:
            error_msg = str(e)
            print(f"   ✗ ERROR: {error_msg[:60]}...")
            
            # If rate limit detected, next query should use proxy
            if '429' in error_msg or 'rate limit' in error_msg.lower():
                print(f"      → Rate limit detected, will use proxy next")
        
        time.sleep(0.5)
    
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    print(f"\nSuccess Rate: {success_count}/{len(queries)} ({success_count/len(queries)*100:.1f}%)")
    print(f"  Via direct connection: {direct_success}")
    print(f"  Via proxy: {proxy_success}")
    print(f"\nFinal engine state:")
    print(f"  Using proxy: {engine._use_proxy}")
    print(f"  Failed without proxy: {engine._failed_without_proxy}")
    
    if success_count >= len(queries) * 0.7:
        print(f"\n✅ DuckDuckGo with proxies is USABLE ({success_count/len(queries)*100:.1f}%)")
        return True
    else:
        print(f"\n⚠️  DuckDuckGo needs improvement ({success_count/len(queries)*100:.1f}%)")
        return False


if __name__ == '__main__':
    success = test_duckduckgo_with_proxies()
    sys.exit(0 if success else 1)
