"""
Performance testing script for pysearx.

This script tests 10 queries against all supported engines and collects
performance metrics including response times, success rates, and rate limiting.

USAGE:
    python test_performance.py [--chart]

This will:
1. Test all 5 search engines with 10 diverse queries
2. Measure response times and success rates
3. Track when rate limiting occurs
4. Save detailed results to performance_results.json in the current directory
5. Print a summary to the console
6. Optionally generate an interactive chart (--chart flag)

REQUIREMENTS:
- Internet connection (to query search engines)
- pysearx installed: pip install -e .
- For charts: pip install plotly

NOTE: The performance results in docs/performance.md are illustrative examples.
Run this script in your own environment to get actual performance data specific
to your network conditions, location, and time of testing.
"""

import time
import json
import os
import sys
from pysearx import search
from pysearx.engines.duckduckgo import DuckDuckGoEngine
from pysearx.engines.google import GoogleEngine
from pysearx.engines.bing import BingEngine
from pysearx.engines.brave import BraveEngine
from pysearx.engines.startpage import StartpageEngine
from pysearx.engines.mojeek import MojeekEngine
from pysearx.engines.qwant import QwantEngine
from pysearx.engines.yahoo import YahooEngine
from pysearx.engines.yep import YepEngine
from pysearx.engines.metager import MetagerEngine
from pysearx.engines.search360 import Search360Engine
from pysearx.engines.searx import SearxEngine
from pysearx.engines.swisscows import SwisscowsEngine
from pysearx.engines.yandex import YandexEngine


# Test queries covering various topics
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


def test_engine_performance(engine, queries):
    """
    Test a single engine with multiple queries and collect metrics.
    
    Args:
        engine: SearchEngine instance to test
        queries: List of query strings to test
        
    Returns:
        Dictionary containing performance metrics
    """
    engine_name = engine.__class__.__name__
    results = {
        'engine': engine_name,
        'total_queries': len(queries),
        'successful_queries': 0,
        'failed_queries': 0,
        'response_times': [],
        'total_results': 0,
        'errors': [],
        'queries_before_throttle': 0
    }
    
    print(f"\nTesting {engine_name}...")
    print("-" * 60)
    
    for i, query in enumerate(queries, 1):
        print(f"Query {i}/{len(queries)}: '{query}'", end=" ... ")
        
        start_time = time.time()
        try:
            # Search with single engine
            query_results = search(query, engines=[engine], max_results=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Check for 0 results - treat as failure
            if len(query_results) == 0:
                results['failed_queries'] += 1
                results['errors'].append({
                    'query': query,
                    'error': 'No results returned',
                    'query_number': i
                })
                print(f"✗ No results returned ({response_time:.2f}s)")
            else:
                results['response_times'].append(response_time)
                results['successful_queries'] += 1
                results['total_results'] += len(query_results)
                results['queries_before_throttle'] = i
                print(f"✓ ({response_time:.2f}s, {len(query_results)} results)")
            
            # Add a small delay between queries to be respectful
            time.sleep(1)
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            results['failed_queries'] += 1
            error_msg = str(e)
            results['errors'].append({
                'query': query,
                'error': error_msg,
                'query_number': i
            })
            
            print(f"✗ Error: {error_msg[:50]}...")
            
            # Check if this looks like rate limiting or HTTP error codes
            error_lower = error_msg.lower()
            if ('timeout' in error_lower or 'too many' in error_lower or 
                '429' in error_msg or '400' in error_msg or '401' in error_msg or 
                '403' in error_msg or '404' in error_msg):
                print(f"  (Rate limiting or HTTP error detected at query {i})")
                break
    
    return results


def calculate_statistics(results):
    """Calculate statistical metrics from performance results."""
    stats = {}
    
    if results['response_times']:
        response_times = sorted(results['response_times'])
        stats['min_response_time'] = min(response_times)
        stats['max_response_time'] = max(response_times)
        stats['avg_response_time'] = sum(response_times) / len(response_times)
        
        # Calculate proper median for even and odd length lists
        n = len(response_times)
        if n % 2 == 0:
            stats['median_response_time'] = (response_times[n // 2 - 1] + response_times[n // 2]) / 2
        else:
            stats['median_response_time'] = response_times[n // 2]
    else:
        stats['min_response_time'] = 0
        stats['max_response_time'] = 0
        stats['avg_response_time'] = 0
        stats['median_response_time'] = 0
    
    stats['success_rate'] = (results['successful_queries'] / results['total_queries'] * 100) if results['total_queries'] > 0 else 0
    stats['avg_results_per_query'] = (results['total_results'] / results['successful_queries']) if results['successful_queries'] > 0 else 0
    
    return stats


def create_performance_chart(results, output_file='performance_chart.html'):
    """Create an interactive performance chart using plotly."""
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        import pandas as pd
    except ImportError:
        print("\nWarning: plotly not installed. Install with: pip install plotly")
        return
    
    # Prepare data for visualization
    engines = []
    success_rates = []
    avg_response_times = []
    avg_results = []
    
    for result in results:
        stats = result['statistics']
        engines.append(result['engine'].replace('Engine', ''))
        success_rates.append(stats['success_rate'])
        avg_response_times.append(stats['avg_response_time'])
        avg_results.append(stats['avg_results_per_query'])
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Success Rate (%)', 'Average Response Time (s)', 
                       'Average Results per Query', 'Queries Completed'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # Success rate
    fig.add_trace(
        go.Bar(x=engines, y=success_rates, name='Success Rate',
               marker_color='green'),
        row=1, col=1
    )
    
    # Response time
    fig.add_trace(
        go.Bar(x=engines, y=avg_response_times, name='Response Time',
               marker_color='blue'),
        row=1, col=2
    )
    
    # Average results
    fig.add_trace(
        go.Bar(x=engines, y=avg_results, name='Avg Results',
               marker_color='orange'),
        row=2, col=1
    )
    
    # Queries completed
    queries_completed = [r['successful_queries'] for r in results]
    fig.add_trace(
        go.Bar(x=engines, y=queries_completed, name='Queries Completed',
               marker_color='purple'),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text='PySearx Performance Metrics',
        showlegend=False,
        height=800
    )
    
    fig.update_xaxes(tickangle=45)
    
    # Save chart
    fig.write_html(output_file)
    print(f"\nInteractive chart saved to: {output_file}")


def main():
    """Run performance tests on all engines."""
    # Check for --chart flag
    generate_chart = '--chart' in sys.argv
    
    print("=" * 60)
    print("PYSEARX PERFORMANCE TESTING")
    print("=" * 60)
    print(f"\nTesting {len(TEST_QUERIES)} queries against all supported engines")
    print(f"Queries: {', '.join(TEST_QUERIES[:3])}, ...")
    if generate_chart:
        print("Chart generation: ENABLED")
    print()
    
    # Initialize all engines
    engines = [
        DuckDuckGoEngine(),
        GoogleEngine(),
        BingEngine(),
        BraveEngine(),
        StartpageEngine(),
        MojeekEngine(),
        QwantEngine(),
        YahooEngine(),
        YepEngine(),
        MetagerEngine(),
        Search360Engine(),
        SearxEngine(),
        SwisscowsEngine(),
        YandexEngine(),
    ]
    
    all_results = []
    
    # Test each engine
    for engine in engines:
        engine_results = test_engine_performance(engine, TEST_QUERIES)
        stats = calculate_statistics(engine_results)
        engine_results['statistics'] = stats
        all_results.append(engine_results)
    
    # Print summary
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    
    for result in all_results:
        stats = result['statistics']
        print(f"\n{result['engine']}:")
        print(f"  Successful queries: {result['successful_queries']}/{result['total_queries']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Queries before throttle/error: {result['queries_before_throttle']}")
        print(f"  Average response time: {stats['avg_response_time']:.2f}s")
        print(f"  Response time range: {stats['min_response_time']:.2f}s - {stats['max_response_time']:.2f}s")
        print(f"  Average results per query: {stats['avg_results_per_query']:.1f}")
        if result['errors']:
            print(f"  Errors encountered: {len(result['errors'])}")
    
    # Save results to JSON in current working directory
    output_file = 'performance_results.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n\nDetailed results saved to: {output_file}")
    print("\nUse this data to update docs/performance.md with your actual results")
    
    # Generate chart if requested
    if generate_chart:
        create_performance_chart(all_results)
    
    return all_results


if __name__ == '__main__':
    main()
