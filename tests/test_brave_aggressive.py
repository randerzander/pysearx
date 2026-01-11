"""
Aggressive test to trigger Brave 429 and test proxy fallback.
"""

import os
import sys
import time

os.environ['PROXY_FILE'] = 'working_proxies.txt'

from pysearx.engines.brave import BraveEngine


def test_brave_until_rate_limit():
    """Test Brave rapidly until we hit 429, then verify proxy fallback."""
    print("=" * 70)
    print("AGGRESSIVE BRAVE TEST - TRIGGER 429 THEN USE PROXIES")
    print("=" * 70)
    
    engine = BraveEngine()
    
    # Many queries in rapid succession
    queries = [f"query {i}" for i in range(50)]
    
    print(f"\nTesting {len(queries)} queries rapidly (no delays)...")
    print("Goal: Trigger 429 rate limit, then switch to proxies")
    print("=" * 70)
    
    successful = 0
    failed = 0
    rate_limited_count = 0
    switched_to_proxy = False
    
    for i, query in enumerate(queries, 1):
        if i % 10 == 0:
            print(f"\nProgress: {i}/{len(queries)} queries...")
        
        try:
            results = engine.search(query)
            
            if results:
                successful += 1
                if i <= 5 or i % 10 == 0:
                    print(f"  {i}. ✓ {len(results)} results" + 
                          (" [WITH PROXY]" if engine._use_proxy else ""))
            else:
                failed += 1
                print(f"  {i}. ⚠️ No results")
        
        except Exception as e:
            error_msg = str(e)
            
            if 'Rate limited' in error_msg or '429' in error_msg:
                rate_limited_count += 1
                if not switched_to_proxy:
                    print(f"\n  🚨 {i}. RATE LIMIT HIT!")
                    print(f"      {error_msg[:70]}...")
                    print(f"      Engine should switch to proxy mode now")
                    switched_to_proxy = True
                else:
                    print(f"  {i}. ⏸️ Still rate limited")
            else:
                failed += 1
                print(f"  {i}. ✗ Error: {error_msg[:50]}...")
        
        # Small delay to avoid too aggressive hammering
        if i < 20:
            time.sleep(0.1)  # Very short delay for first 20
    
    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\nTotal queries: {len(queries)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Rate limited: {rate_limited_count}")
    print(f"Success rate: {successful/len(queries)*100:.1f}%")
    
    print(f"\nEngine final state:")
    print(f"  Using proxy: {engine._use_proxy}")
    print(f"  Failed without proxy: {engine._failed_without_proxy}")
    
    if rate_limited_count > 0:
        print(f"\n✅ SUCCESS: Triggered {rate_limited_count} rate limit(s)")
        if engine._use_proxy:
            print("   ✅ Engine switched to proxy mode as expected")
        else:
            print("   ⚠️ Engine didn't switch to proxy mode (unexpected)")
    else:
        print(f"\n⚠️ Never triggered rate limit in {len(queries)} queries")
        print("   Brave may have high rate limits or we're not aggressive enough")
    
    if successful > 0:
        print(f"\n🎉 Got {successful} successful results!")
    
    return successful > 0


if __name__ == '__main__':
    success = test_brave_until_rate_limit()
    sys.exit(0 if success else 1)
