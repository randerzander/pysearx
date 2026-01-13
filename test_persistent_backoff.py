#!/usr/bin/env python3
"""
Test that exponential backoff persists across multiple queries.
This simulates the scenario from the issue where Mojeek was getting
repeated 403 errors but always showing "Attempt #1".
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from pysearx.engines.mojeek import MojeekEngine


def test_persistent_backoff():
    """Test that backoff state persists across queries."""
    print("=" * 70)
    print("TESTING PERSISTENT BACKOFF ACROSS QUERIES")
    print("=" * 70)
    
    # Create a single engine instance (simulating DEFAULT_ENGINES)
    engine = MojeekEngine()
    
    print("\nSimulating multiple queries to Mojeek that all fail with 403...")
    print("Expected: Backoff should increase each time (1s, 2s, 4s, 8s...)\n")
    
    # Simulate 5 failed queries
    for query_num in range(1, 6):
        print(f"Query {query_num}:")
        print(f"  - Rate limit count before query: {engine._rate_limit_count}")
        
        # Simulate a rate limit error
        engine._handle_rate_limit()
        
        print(f"  - Rate limit count after handling: {engine._rate_limit_count}")
        print(f"  - Backoff time: {int(engine._rate_limited_until - time.time())}s")
        
        # Wait for backoff to expire (or simulate it)
        engine._rate_limited_until = time.time() - 1  # Expired
        
        # Check rate limit (should not reset count)
        try:
            engine._check_rate_limit()
        except:
            pass
        
        print(f"  - Count after backoff expiry: {engine._rate_limit_count}")
        print()
    
    print("=" * 70)
    print("RESULT")
    print("=" * 70)
    
    if engine._rate_limit_count == 5:
        print("\n✅ SUCCESS! Backoff persisted across all 5 queries")
        print("   - Count increased each time: 1 → 2 → 3 → 4 → 5")
        print("   - This means backoff times increased: 1s → 2s → 4s → 8s → 16s")
        print("   - The fix is working correctly!")
        return True
    else:
        print(f"\n❌ FAILED! Expected count=5, got count={engine._rate_limit_count}")
        return False


def test_reset_on_success():
    """Test that backoff resets after a successful request."""
    print("\n" + "=" * 70)
    print("TESTING RESET ON SUCCESS")
    print("=" * 70)
    
    engine = MojeekEngine()
    
    # Simulate 3 failures
    for i in range(3):
        engine._handle_rate_limit()
        engine._rate_limited_until = 0
    
    print(f"\nAfter 3 failures, count = {engine._rate_limit_count}")
    
    # Simulate successful request
    engine._reset_rate_limit()
    
    print(f"After successful request, count = {engine._rate_limit_count}")
    
    if engine._rate_limit_count == 0:
        print("\n✅ SUCCESS! Counter resets to 0 after successful request")
        return True
    else:
        print(f"\n❌ FAILED! Expected count=0, got count={engine._rate_limit_count}")
        return False


if __name__ == '__main__':
    test1 = test_persistent_backoff()
    test2 = test_reset_on_success()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if test1 and test2:
        print("\n✅ ALL TESTS PASSED")
        print("\nThe fix ensures that:")
        print("  1. Backoff persists across queries (no reset on expiry)")
        print("  2. Backoff only resets on successful requests")
        print("  3. This prevents repeatedly hitting rate-limited services")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
