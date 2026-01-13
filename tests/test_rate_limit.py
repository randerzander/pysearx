"""
Test script for rate limit backoff functionality.

Tests that engines properly handle 429 errors by:
1. Detecting rate limit errors
2. Setting backoff timer
3. Rejecting requests during backoff period
4. Allowing requests after backoff expires
"""

import time
from unittest.mock import Mock, patch
import requests

from pysearx.engines.brave import BraveEngine
from pysearx.engines.duckduckgo import DuckDuckGoEngine
from pysearx.engines.google import GoogleEngine


def test_rate_limit_detection():
    """Test that rate limit errors are properly detected."""
    print("=" * 70)
    print("TEST: Rate Limit Detection")
    print("=" * 70)
    
    engine = BraveEngine()
    
    test_cases = [
        ("429 Client Error: Too Many Requests", True),
        ("Rate limit exceeded", True),
        ("Too many requests from your IP", True),
        ("403 Forbidden", True),  # 403 is treated as blocking/rate limit
        ("Connection timeout", False),
    ]
    
    for error_msg, expected in test_cases:
        result = engine._is_rate_limit_error(error_msg)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{error_msg}' -> {result} (expected {expected})")
    
    print()


def test_rate_limit_backoff():
    """Test that backoff timer works correctly."""
    print("=" * 70)
    print("TEST: Rate Limit Backoff Timer")
    print("=" * 70)
    
    engine = BraveEngine()
    
    # Initially should not be rate limited
    try:
        engine._check_rate_limit()
        print("✓ Initially not rate limited")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return
    
    # Trigger rate limit
    engine._handle_rate_limit()
    # Calculate expected backoff time
    expected_backoff = engine._base_backoff * (2 ** (engine._rate_limit_count - 1))
    print(f"✓ Rate limit triggered (backoff: {expected_backoff}s)")
    
    # Should now be rate limited
    try:
        engine._check_rate_limit()
        print("✗ Should have been rate limited")
    except Exception as e:
        if "Rate limited" in str(e):
            print(f"✓ Correctly blocked: {e}")
        else:
            print(f"✗ Wrong error: {e}")
    
    # Wait a bit and check again
    print("\n  Waiting 2 seconds...")
    time.sleep(2)
    
    try:
        engine._check_rate_limit()
        print("✗ Should still be rate limited")
    except Exception as e:
        if "Rate limited" in str(e):
            remaining = int(str(e).split()[-2])
            print(f"✓ Still blocked ({remaining}s remaining)")
        else:
            print(f"✗ Wrong error: {e}")
    
    print()


def test_rate_limit_recovery():
    """Test that engine recovers after backoff period."""
    print("=" * 70)
    print("TEST: Rate Limit Recovery")
    print("=" * 70)
    
    engine = DuckDuckGoEngine()
    
    # Set short backoff for testing
    engine._backoff_seconds = 3
    
    # Trigger rate limit
    engine._handle_rate_limit()
    print("✓ Rate limit triggered (3s backoff)")
    
    # Should be blocked
    try:
        engine._check_rate_limit()
        print("✗ Should be blocked")
    except Exception as e:
        print(f"✓ Blocked: {e}")
    
    # Wait for backoff to expire
    print("\n  Waiting 4 seconds for backoff to expire...")
    time.sleep(4)
    
    # Should now work
    try:
        engine._check_rate_limit()
        print("✓ Recovered - no longer rate limited")
    except Exception as e:
        print(f"✗ Should have recovered: {e}")
    
    print()


def test_engine_integration():
    """Test that rate limit integrates with actual search call."""
    print("=" * 70)
    print("TEST: Integration with Search Method")
    print("=" * 70)
    
    engine = GoogleEngine()
    engine._backoff_seconds = 2
    
    # Mock requests to simulate 429 error
    with patch('requests.get') as mock_get:
        # First call returns 429
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("429 Client Error: Too Many Requests")
        mock_get.return_value = mock_response
        
        try:
            engine.search("test query")
            print("✗ Should have raised exception")
        except Exception as e:
            if "429" in str(e):
                print(f"✓ First call raised 429 error: {e}")
            else:
                print(f"✗ Wrong error: {e}")
    
    # Second call should be blocked by backoff
    print("\n  Immediate retry should be blocked...")
    try:
        engine.search("test query")
        print("✗ Should have been rate limited")
    except Exception as e:
        if "Rate limited" in str(e):
            print(f"✓ Second call blocked by backoff: {e}")
        else:
            print(f"✗ Wrong error: {e}")
    
    # After backoff, should allow retry
    print(f"\n  Waiting {engine._backoff_seconds + 1} seconds...")
    time.sleep(engine._backoff_seconds + 1)
    
    with patch('requests.get') as mock_get:
        # This time return success
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'<html></html>'
        mock_get.return_value = mock_response
        
        try:
            results = engine.search("test query")
            print(f"✓ Third call succeeded after backoff (returned {len(results)} results)")
        except Exception as e:
            # Might fail due to parsing, but should get past rate limit
            if "Rate limited" not in str(e):
                print(f"✓ Not blocked by rate limit (parse error is OK)")
            else:
                print(f"✗ Still rate limited: {e}")
    
    print()


def test_multiple_engines_independent():
    """Test that rate limits are independent per engine."""
    print("=" * 70)
    print("TEST: Independent Rate Limits Per Engine")
    print("=" * 70)
    
    brave = BraveEngine()
    ddg = DuckDuckGoEngine()
    
    # Rate limit Brave
    brave._handle_rate_limit()
    print("✓ Brave rate limited")
    
    # Brave should be blocked
    try:
        brave._check_rate_limit()
        print("✗ Brave should be blocked")
    except Exception as e:
        print(f"✓ Brave blocked: {e}")
    
    # DuckDuckGo should still work
    try:
        ddg._check_rate_limit()
        print("✓ DuckDuckGo not affected")
    except Exception as e:
        print(f"✗ DuckDuckGo should work: {e}")
    
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("RATE LIMIT BACKOFF TEST SUITE")
    print("=" * 70 + "\n")
    
    test_rate_limit_detection()
    test_rate_limit_backoff()
    test_rate_limit_recovery()
    test_engine_integration()
    test_multiple_engines_independent()
    
    print("=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)


if __name__ == '__main__':
    main()
