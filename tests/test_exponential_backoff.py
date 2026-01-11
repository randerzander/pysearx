"""
Test exponential backoff rate limiting.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from pysearx.base import RateLimitMixin


class TestEngine(RateLimitMixin):
    """Test engine to demonstrate exponential backoff."""
    
    def __init__(self):
        RateLimitMixin.__init__(self)
        self.name = 'TestEngine'


def test_exponential_backoff():
    """Test that exponential backoff increases properly."""
    print("=" * 70)
    print("TESTING EXPONENTIAL BACKOFF")
    print("=" * 70)
    
    engine = TestEngine()
    
    print("\nSimulating consecutive rate limit hits...")
    print("Expected backoff pattern: 1s, 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 300s (max)")
    print()
    
    backoff_times = []
    
    for i in range(12):
        # Trigger rate limit
        engine._handle_rate_limit()
        
        # Calculate actual backoff
        if engine._rate_limited_until > 0:
            backoff = int(engine._rate_limited_until - time.time())
            backoff_times.append(backoff)
            
            print(f"Rate limit #{i+1}: Backoff = {backoff}s")
        
        # Simulate time passing (so we don't actually wait)
        engine._rate_limited_until = 0  # Reset for next iteration
    
    print("\n" + "=" * 70)
    print("BACKOFF PROGRESSION")
    print("=" * 70)
    
    expected = [1, 2, 4, 8, 16, 32, 64, 128, 256, 300, 300, 300]
    
    print("\nAttempt | Expected | Actual | Status")
    print("-" * 70)
    for i, (exp, act) in enumerate(zip(expected, backoff_times), 1):
        # Allow 1 second tolerance for timing
        status = "✓" if abs(exp - act) <= 1 else "✗"
        print(f"   {i:2d}   |   {exp:3d}s   |  {act:3d}s  | {status}")
    
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    # Check if all are within 1 second tolerance
    all_within_tolerance = all(abs(exp - act) <= 1 for exp, act in zip(expected, backoff_times))
    
    if all_within_tolerance:
        print("\n✅ Exponential backoff working correctly!")
        print("   - Doubles each attempt: 1, 2, 4, 8, 16, 32, 64, 128, 256")
        print("   - Caps at 300s (5 minutes)")
        print("   - All values within expected tolerance")
    else:
        print("\n⚠️  Backoff doesn't match expected pattern")
    
    # Test reset after successful request
    print("\n" + "=" * 70)
    print("TESTING RESET AFTER SUCCESS")
    print("=" * 70)
    
    engine2 = TestEngine()
    
    # Hit rate limit a few times
    for i in range(3):
        engine2._handle_rate_limit()
        engine2._rate_limited_until = 0  # Simulate time passing
    
    print(f"\nAfter 3 rate limits, count = {engine2._rate_limit_count}")
    
    # Simulate successful request (rate limit expires)
    engine2._rate_limited_until = time.time() - 1  # Expired
    try:
        engine2._check_rate_limit()
        print(f"After expiration, count reset to: {engine2._rate_limit_count}")
        
        if engine2._rate_limit_count == 0:
            print("✅ Counter successfully resets after backoff expires")
        else:
            print("⚠️  Counter didn't reset")
    except:
        print("⚠️  Unexpected error")
    
    print("\n" + "=" * 70)
    
    return all_within_tolerance


if __name__ == '__main__':
    success = test_exponential_backoff()
    sys.exit(0 if success else 1)
