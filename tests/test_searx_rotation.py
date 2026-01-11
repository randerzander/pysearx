"""
Standalone test for SearX engine with instance rotation.

Tests the updated SearX engine that:
- Automatically loads public instances from searx.space
- Rotates through instances on each search
- Removes failed instances from the pool
"""

import time
from pysearx.engines.searx import SearxEngine

# Test queries from performance test
TEST_QUERIES = [
    "python programming",
    "machine learning",
    "web development",
    "data science",
    "artificial intelligence",
    "cloud computing",
    "cybersecurity",
    "blockchain technology",
    "quantum computing",
    "natural language processing"
]


def test_searx_with_rotation():
    """Test SearX engine with automatic instance rotation."""
    print("=" * 70)
    print("SEARX ENGINE STANDALONE TEST")
    print("=" * 70)
    print("\nThis test will:")
    print("1. Load public SearXNG instances from searx.space")
    print("2. Rotate through instances for each query")
    print("3. Remove failed instances automatically")
    print("4. Retry up to 3 times per query with different instances")
    print()
    
    # Initialize engine (this will load instances)
    print("Initializing SearX engine...")
    engine = SearxEngine()
    print()
    
    # Track which instances succeeded
    successful_instances = set()
    
    # Test statistics
    total_queries = len(TEST_QUERIES)
    successful = 0
    failed = 0
    total_results = 0
    response_times = []
    
    print(f"Running {total_queries} test queries...")
    print("-" * 70)
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{i}. Query: '{query}'")
        
        # Get instance before search
        instance_before = SearxEngine._current_index
        
        start_time = time.time()
        try:
            results = engine.search(query)
            end_time = time.time()
            response_time = end_time - start_time
            
            # Figure out which instance succeeded
            if SearxEngine._instances:
                used_instance = SearxEngine._instances[(instance_before) % len(SearxEngine._instances)]
                successful_instances.add(used_instance)
            
            if results:
                successful += 1
                total_results += len(results)
                response_times.append(response_time)
                
                print(f"   ✓ Success: {len(results)} results in {response_time:.2f}s")
                
                # Show first 3 results
                for j, result in enumerate(results[:3], 1):
                    print(f"      {j}. {result['title'][:60]}...")
                    print(f"         {result['url']}")
            else:
                failed += 1
                print(f"   ✗ No results returned ({response_time:.2f}s)")
            
            # Small delay to be respectful
            time.sleep(1)
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            failed += 1
            error_msg = str(e)
            print(f"   ✗ Error: {error_msg[:80]}...")
            print(f"      (after {response_time:.2f}s)")
            
            # Continue to next query even after errors
            time.sleep(1)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\nTotal queries:      {total_queries}")
    print(f"Successful:         {successful}")
    print(f"Failed:             {failed}")
    print(f"Success rate:       {(successful/total_queries*100):.1f}%")
    print(f"Total results:      {total_results}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        print(f"\nAverage time:       {avg_time:.2f}s")
        print(f"Min time:           {min_time:.2f}s")
        print(f"Max time:           {max_time:.2f}s")
        print(f"Avg results/query:  {total_results/successful:.1f}" if successful > 0 else "")
    
    # Check instance pool status
    if SearxEngine._instances:
        print(f"\nStarted with:       68 instances")
        print(f"Remaining:          {len(SearxEngine._instances)} instances")
        print(f"Removed:            {68 - len(SearxEngine._instances)} instances")
        
        if successful_instances:
            print(f"\n✓ Working instances found: {len(successful_instances)}")
            for inst in list(successful_instances)[:5]:
                print(f"  - {inst}")
    
    print("\n" + "=" * 70)
    
    return {
        'total': total_queries,
        'successful': successful,
        'failed': failed,
        'success_rate': (successful/total_queries*100) if total_queries > 0 else 0,
        'total_results': total_results,
        'response_times': response_times,
        'working_instances': successful_instances
    }


if __name__ == '__main__':
    results = test_searx_with_rotation()
    
    # Exit code based on success rate
    if results['success_rate'] >= 50:
        print("\n✓ Test passed (>= 50% success rate)")
        exit(0)
    else:
        print(f"\n✗ Test failed (< 50% success rate)")
        exit(1)
