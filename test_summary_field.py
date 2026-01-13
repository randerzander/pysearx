#!/usr/bin/env python3
"""
Test script to demonstrate the new 'summary' field in search results.

This script tests that all search engines return both 'summary' and 'description'
fields (with 'description' deprecated in favor of 'summary').
"""

from pysearx import search
from pysearx.engines.duckduckgo_api import DuckDuckGoAPIEngine
from pysearx.engines.yahoo import YahooEngine
from pysearx.engines.mojeek import MojeekEngine


def test_summary_field():
    """Test that search results include the 'summary' field."""
    print("Testing search results for 'summary' field...\n")
    
    # Test with default engines
    print("=" * 70)
    print("Test 1: Default engines")
    print("=" * 70)
    results = search("python programming", max_results=2)
    
    if results:
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Engine: {result.get('engine', 'N/A')}")
            print(f"  Title: {result.get('title', 'N/A')[:60]}...")
            print(f"  URL: {result.get('url', 'N/A')[:60]}...")
            
            # Check for both fields
            has_summary = 'summary' in result
            has_description = 'description' in result
            
            print(f"  Has 'summary': {has_summary}")
            print(f"  Has 'description': {has_description}")
            
            if has_summary and has_description:
                summary_preview = result['summary'][:100] if result['summary'] else ''
                print(f"  Summary preview: {summary_preview}...")
                print(f"  Summary length: {len(result.get('summary', ''))}")
                print(f"  ✓ Both fields present and equal: {result['summary'] == result['description']}")
            else:
                print(f"  ✗ Missing required fields!")
    else:
        print("  No results found")
    
    # Test individual engines
    engines_to_test = [
        ("DuckDuckGo API", DuckDuckGoAPIEngine()),
        ("Yahoo", YahooEngine()),
        ("Mojeek", MojeekEngine()),
    ]
    
    for engine_name, engine in engines_to_test:
        print(f"\n{'=' * 70}")
        print(f"Test 2: {engine_name} Engine")
        print("=" * 70)
        
        try:
            results = search("python", engines=[engine], max_results=1)
            
            if results:
                result = results[0]
                print(f"  Title: {result.get('title', 'N/A')[:60]}...")
                print(f"  Has 'summary': {'summary' in result}")
                print(f"  Has 'description': {'description' in result}")
                print(f"  Summary length: {len(result.get('summary', ''))}")
                
                if 'summary' in result and 'description' in result:
                    print(f"  ✓ Both fields present")
                else:
                    print(f"  ✗ Missing required fields!")
            else:
                print(f"  No results found from {engine_name}")
                
        except Exception as e:
            print(f"  Error testing {engine_name}: {e}")
    
    print("\n" + "=" * 70)
    print("Summary Field Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    test_summary_field()
