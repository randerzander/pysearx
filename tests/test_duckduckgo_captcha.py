"""
Detailed DuckDuckGo test to analyze CAPTCHA blocking patterns.

Tests:
1. Does DDG return results normally?
2. When does CAPTCHA blocking start?
3. Is CAPTCHA blocking consistent or intermittent?
4. Can retries work around intermittent CAPTCHAs?
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from pysearx.engines.duckduckgo import DuckDuckGoEngine


def test_duckduckgo_captcha_patterns():
    """Detailed test of DuckDuckGo CAPTCHA behavior."""
    print("=" * 80)
    print("DUCKDUCKGO CAPTCHA PATTERN ANALYSIS")
    print("=" * 80)
    
    engine = DuckDuckGoEngine()
    
    queries = [
        "python programming",
        "javascript tutorial", 
        "golang best practices",
        "rust programming language",
        "kotlin android development",
        "swift ios development",
        "typescript guide",
        "ruby on rails",
        "php frameworks",
        "java spring boot",
        "c++ modern features",
        "scala functional programming",
        "elixir phoenix",
        "clojure programming",
        "haskell tutorial",
        "perl scripting",
        "lua programming",
        "r data science",
        "julia scientific computing",
        "dart flutter",
    ]
    
    print(f"\nTesting {len(queries)} queries with detailed analysis...")
    print("Looking for patterns in:")
    print("  - Successful results")
    print("  - Empty results (possible CAPTCHA)")
    print("  - Errors")
    print("  - Retry behavior")
    print()
    
    results_log = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        # Try initial request
        try:
            results = engine.search(query)
            
            if results and len(results) > 0:
                print(f"   ✓ SUCCESS: {len(results)} results")
                print(f"      First result: {results[0]['title'][:60]}...")
                results_log.append({
                    'query': query,
                    'attempt': 1,
                    'status': 'success',
                    'count': len(results)
                })
            else:
                print(f"   ⚠️  EMPTY RESULTS (possible CAPTCHA)")
                results_log.append({
                    'query': query,
                    'attempt': 1,
                    'status': 'empty',
                    'count': 0
                })
                
                # Try a retry after short delay
                print(f"      Retrying after 2 seconds...")
                time.sleep(2)
                
                try:
                    retry_results = engine.search(query)
                    if retry_results and len(retry_results) > 0:
                        print(f"      ✓ RETRY SUCCESS: {len(retry_results)} results")
                        print(f"         → Intermittent CAPTCHA (retry worked)")
                        results_log.append({
                            'query': query,
                            'attempt': 2,
                            'status': 'retry_success',
                            'count': len(retry_results)
                        })
                    else:
                        print(f"      ✗ RETRY FAILED: Still empty")
                        print(f"         → Consistent CAPTCHA (retry didn't help)")
                        results_log.append({
                            'query': query,
                            'attempt': 2,
                            'status': 'retry_empty',
                            'count': 0
                        })
                except Exception as e:
                    print(f"      ✗ RETRY ERROR: {str(e)[:50]}...")
                    results_log.append({
                        'query': query,
                        'attempt': 2,
                        'status': 'retry_error',
                        'error': str(e)[:100]
                    })
        
        except Exception as e:
            error_msg = str(e)
            print(f"   ✗ ERROR: {error_msg[:60]}...")
            
            if 'captcha' in error_msg.lower():
                print(f"      → Explicit CAPTCHA error")
            elif 'rate limit' in error_msg.lower() or '429' in error_msg:
                print(f"      → Rate limit error")
            elif 'timeout' in error_msg.lower():
                print(f"      → Timeout error")
            else:
                print(f"      → Other error")
            
            results_log.append({
                'query': query,
                'attempt': 1,
                'status': 'error',
                'error': error_msg[:100]
            })
        
        # Small delay between queries
        if i < len(queries):
            time.sleep(1)
    
    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    
    # Count outcomes
    success_count = sum(1 for r in results_log if r['status'] == 'success')
    empty_count = sum(1 for r in results_log if r['status'] == 'empty')
    retry_success_count = sum(1 for r in results_log if r['status'] == 'retry_success')
    retry_failed_count = sum(1 for r in results_log if r['status'] == 'retry_empty')
    error_count = sum(1 for r in results_log if r['status'] in ['error', 'retry_error'])
    
    total_queries = len(queries)
    total_attempts = len(results_log)
    
    print(f"\nFirst Attempt Results:")
    print(f"  Success: {success_count}/{total_queries} ({success_count/total_queries*100:.1f}%)")
    print(f"  Empty (possible CAPTCHA): {empty_count}/{total_queries} ({empty_count/total_queries*100:.1f}%)")
    print(f"  Errors: {error_count}/{total_queries} ({error_count/total_queries*100:.1f}%)")
    
    if empty_count > 0:
        print(f"\nRetry Analysis:")
        print(f"  Retry succeeded: {retry_success_count}/{empty_count} ({retry_success_count/empty_count*100:.1f}%)")
        print(f"  Retry failed: {retry_failed_count}/{empty_count} ({retry_failed_count/empty_count*100:.1f}%)")
        
        if retry_success_count > 0:
            print(f"\n✅ INTERMITTENT CAPTCHA DETECTED!")
            print(f"   {retry_success_count} queries succeeded on retry")
            print(f"   → Retry strategy could be effective")
        else:
            print(f"\n⚠️  CONSISTENT BLOCKING DETECTED")
            print(f"   No retries succeeded")
            print(f"   → Retry strategy may not help")
    
    # Pattern detection
    print(f"\nPattern Detection:")
    
    # Check if failures started after N successes
    first_empty_idx = next((i for i, r in enumerate(results_log) 
                           if r['status'] == 'empty'), None)
    if first_empty_idx:
        successes_before_empty = sum(1 for r in results_log[:first_empty_idx] 
                                     if r['status'] == 'success')
        print(f"  First empty result after {successes_before_empty} successful queries")
        print(f"  → Suggests rate limiting kicks in after ~{successes_before_empty} queries")
    else:
        print(f"  No empty results detected")
    
    # Overall effectiveness
    print(f"\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    total_successful = success_count + retry_success_count
    
    print(f"\nOverall Success Rate:")
    print(f"  Without retries: {success_count}/{total_queries} ({success_count/total_queries*100:.1f}%)")
    print(f"  With retries: {total_successful}/{total_queries} ({total_successful/total_queries*100:.1f}%)")
    
    if retry_success_count > 0:
        improvement = ((total_successful - success_count) / total_queries) * 100
        print(f"  Improvement from retries: +{improvement:.1f}%")
        print(f"\n✅ RECOMMENDATION: Implement retry logic for empty results")
    else:
        print(f"\n⚠️  RECOMMENDATION: Retries don't help, consider alternative approach")
    
    # Check if DDG is usable
    if total_successful >= total_queries * 0.7:  # 70% success threshold
        print(f"\n✅ DuckDuckGo is USABLE ({total_successful/total_queries*100:.1f}% success rate)")
    elif total_successful >= total_queries * 0.3:  # 30% success threshold
        print(f"\n⚠️  DuckDuckGo is PARTIALLY USABLE ({total_successful/total_queries*100:.1f}% success rate)")
    else:
        print(f"\n❌ DuckDuckGo is NOT USABLE ({total_successful/total_queries*100:.1f}% success rate)")
    
    print("\n" + "=" * 80)
    
    return total_successful / total_queries >= 0.5


if __name__ == '__main__':
    success = test_duckduckgo_captcha_patterns()
    sys.exit(0 if success else 1)
