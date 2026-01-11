"""
Utility script to fetch and list all public SearXNG instances from searx.space.

This script fetches the list of public SearXNG instances from searx.space
and provides utilities to filter and select working instances.
"""

import requests
import json
from typing import List, Dict, Any, Optional


def fetch_instances(timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch the list of public SearXNG instances from searx.space.
    
    Args:
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing instance data and metadata
    """
    url = "https://searx.space/data/instances.json"
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch SearXNG instances: {e}")


def get_working_instances(
    min_success_rate: float = 80.0,
    require_https: bool = True,
    exclude_cloudflare: bool = True
) -> List[Dict[str, Any]]:
    """
    Get a filtered list of working SearXNG instances.
    
    Args:
        min_success_rate: Minimum success percentage for initial page load
        require_https: Only return HTTPS instances
        exclude_cloudflare: Exclude instances behind Cloudflare
        
    Returns:
        List of instance dictionaries with url, version, and timing info
    """
    data = fetch_instances()
    instances = data.get('instances', {})
    working = []
    
    for url, info in instances.items():
        # Check if it's HTTPS
        if require_https and not url.startswith('https://'):
            continue
        
        # Check if behind Cloudflare
        network_type = info.get('network_type', '')
        if exclude_cloudflare and network_type == 'cloudflare':
            continue
        
        # Check HTTP status
        http_info = info.get('http', {})
        if http_info.get('status_code') != 200:
            continue
        
        # Check success rate
        timing = info.get('timing', {})
        initial = timing.get('initial', {})
        success_pct = initial.get('success_percentage', 0)
        
        if success_pct < min_success_rate:
            continue
        
        # Check if it's actually SearXNG (not old SearX)
        generator = info.get('generator', '')
        if generator != 'searxng':
            continue
        
        working.append({
            'url': url,
            'version': info.get('version', 'unknown'),
            'network_type': network_type,
            'success_percentage': success_pct,
            'response_time': initial.get('all', {}).get('value', 0),
            'tls_grade': info.get('tls', {}).get('grade', 'N/A'),
        })
    
    # Sort by success rate and response time
    working.sort(key=lambda x: (-x['success_percentage'], x['response_time']))
    
    return working


def get_best_instance() -> Optional[str]:
    """
    Get the best available SearXNG instance URL.
    
    Returns:
        URL of the best instance, or None if no instances are available
    """
    instances = get_working_instances()
    if instances:
        return instances[0]['url']
    return None


def main():
    """Main function to display working instances."""
    print("Fetching SearXNG instances from searx.space...\n")
    
    try:
        instances = get_working_instances()
        
        print(f"Found {len(instances)} working SearXNG instances:\n")
        print(f"{'URL':<50} {'Success %':<12} {'Response (s)':<15} {'TLS Grade':<10}")
        print("-" * 90)
        
        for instance in instances[:20]:  # Show top 20
            url = instance['url']
            success = instance['success_percentage']
            response = instance['response_time']
            tls = instance['tls_grade']
            
            print(f"{url:<50} {success:<12.1f} {response:<15.3f} {tls:<10}")
        
        if len(instances) > 20:
            print(f"\n... and {len(instances) - 20} more instances")
        
        print(f"\nBest instance: {get_best_instance()}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
