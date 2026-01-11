"""
Test disabled engines with proxy support.
"""

import os
import sys

# Set proxy file
os.environ['PROXY_FILE'] = 'working_proxies.txt'

from pysearx.engines.google import GoogleEngine
from pysearx.engines.startpage import StartpageEngine
from pysearx.engines.qwant import QwantEngine
from pysearx.engines.yep import YepEngine


def test_engine(engine, query="python programming"):
    """Test a single engine with proxies."""
    print(f"\nTesting {engine.name}...")
    print("-" * 70)
    
    try:
        results = engine.search(query)
        
        if results:
            print(f"✓ SUCCESS: {len(results)} results")
            print(f"  1. {results[0]['title'][:60]}...")
            print(f"     {results[0]['url'][:70]}...")
            return True, len(results)
        else:
            print(f"✗ No results (likely CAPTCHA or parsing issue)")
            return False, 0
    except Exception as e:
        error_msg = str(e)
        if 'captcha' in error_msg.lower() or 'robot' in error_msg.lower():
            print(f"✗ CAPTCHA detected")
        elif '403' in error_msg or 'Forbidden' in error_msg:
            print(f"✗ 403 Forbidden")
        elif 'Rate limited' in error_msg:
            print(f"✗ {error_msg}")
        else:
            print(f"✗ Error: {error_msg[:80]}...")
        return False, 0


def main():
    print("=" * 70)
    print("TESTING DISABLED ENGINES WITH PROXIES")
    print("=" * 70)
    print(f"\nPROXY_FILE={os.getenv('PROXY_FILE')}")
    
    # Engines to test
    engines = [
        GoogleEngine(),
        StartpageEngine(),
        QwantEngine(),
        YepEngine(),
    ]
    
    queries = [
        "python programming",
        "machine learning",
        "web development"
    ]
    
    results = {}
    
    for query in queries:
        print(f"\n\n{'=' * 70}")
        print(f"QUERY: '{query}'")
        print("=" * 70)
        
        for engine in engines:
            success, count = test_engine(engine, query)
            
            if engine.name not in results:
                results[engine.name] = {'success': 0, 'total': 0, 'results': 0}
            
            results[engine.name]['total'] += 1
            if success:
                results[engine.name]['success'] += 1
                results[engine.name]['results'] += count
    
    # Summary
    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for engine_name, stats in results.items():
        success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"\n{engine_name}:")
        print(f"  Success: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        if stats['success'] > 0:
            avg_results = stats['results'] / stats['success']
            print(f"  Avg results: {avg_results:.1f}")
            print(f"  ✅ Working with proxies!")
    
    # Check if any worked
    any_success = any(s['success'] > 0 for s in results.values())
    
    print("\n" + "=" * 70)
    if any_success:
        print("✅ Some engines work with proxies!")
    else:
        print("⚠️  No engines worked - all proxies blocked or engines broken")
    print("=" * 70)
    
    return any_success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
