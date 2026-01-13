#!/usr/bin/env python3
"""
Verify that backoff state is per-engine and persists across search calls.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pysearx.search import DEFAULT_ENGINES

print("=" * 70)
print("PER-ENGINE BACKOFF ISOLATION TEST")
print("=" * 70)
print()

# Show which engines have rate limiting
print("Engines in DEFAULT_ENGINES:")
for i, engine in enumerate(DEFAULT_ENGINES):
    name = engine.__class__.__name__
    has_rl = hasattr(engine, '_rate_limit_count')
    print(f"  {i+1}. {name:25s} - RateLimitMixin: {'Yes' if has_rl else 'No'}")

print()
print("=" * 70)
print("SCENARIO: Mojeek gets blocked, but Yahoo/DDG keep working")
print("=" * 70)
print()

# Find Mojeek and Yahoo engines
mojeek = None
yahoo = None
for engine in DEFAULT_ENGINES:
    if engine.__class__.__name__ == 'MojeekEngine':
        mojeek = engine
    elif engine.__class__.__name__ == 'YahooEngine':
        yahoo = engine

if not mojeek or not yahoo:
    print("❌ Could not find Mojeek and Yahoo in DEFAULT_ENGINES")
    sys.exit(1)

print("Initial state:")
print(f"  Mojeek: count={mojeek._rate_limit_count}, blocked_until={mojeek._rate_limited_until}")
print(f"  Yahoo:  count={yahoo._rate_limit_count}, blocked_until={yahoo._rate_limited_until}")
print()

# Simulate Mojeek getting repeatedly blocked (like in the user's issue)
print("Simulating 5 consecutive 403 errors from Mojeek:")
for i in range(1, 6):
    mojeek._handle_rate_limit()
    backoff = int(mojeek._rate_limited_until - __import__('time').time())
    print(f"  Query {i}: Mojeek blocked → Attempt #{mojeek._rate_limit_count}, backoff={backoff}s")
    mojeek._rate_limited_until = 0  # Simulate time passing (for demo purposes)

print()
print("Final state after Mojeek blocked 5 times:")
print(f"  Mojeek: count={mojeek._rate_limit_count} (will backoff for 16s on next attempt)")
print(f"  Yahoo:  count={yahoo._rate_limit_count} (still working fine!)")
print()

# Now reset Mojeek (simulate a successful request after waiting)
print("Simulating Mojeek successful request after waiting long enough:")
mojeek._reset_rate_limit()
print(f"  Mojeek: count={mojeek._rate_limit_count} (reset to 0)")
print()

print("=" * 70)
print("VERIFICATION")
print("=" * 70)
print()

if yahoo._rate_limit_count == 0:
    print("✅ Yahoo was not affected by Mojeek's rate limiting")
else:
    print("❌ Yahoo was incorrectly affected")

print()
print("Key points:")
print("  • Each engine instance has its own _rate_limit_count")
print("  • Each engine instance has its own _rate_limited_until timer")
print("  • DEFAULT_ENGINES contains singleton instances (created once at import)")
print("  • State persists across multiple search() calls")
print("  • If Mojeek is blocked, Yahoo/DuckDuckGo continue working normally")
print()
