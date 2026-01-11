#!/usr/bin/env python3
"""
Utility to fetch HTTP proxies from TheSpeedX/PROXY-List and create a whitelist.

Fetches proxies from GitHub, tests each one, and saves working proxies
to a timestamped whitelist file.
"""

import requests
import concurrent.futures
from datetime import datetime
import os
import sys

# Add parent directory to path to import pysearx
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
]

TEST_URL = "https://www.bing.com/search?q=test"
TEST_TIMEOUT = 10
MAX_WORKERS = 20


def fetch_proxies():
    """Fetch proxy lists from GitHub."""
    print("Fetching proxies from TheSpeedX/PROXY-List...")
    all_proxies = []
    
    for source in PROXY_SOURCES:
        try:
            response = requests.get(source, timeout=30)
            if response.status_code == 200:
                proxies = [line.strip() for line in response.text.split('\n') if line.strip()]
                print(f"  Fetched {len(proxies)} proxies from {source.split('/')[-1]}")
                all_proxies.extend(proxies)
        except Exception as e:
            print(f"  Failed to fetch {source}: {e}")
    
    # Remove duplicates
    all_proxies = list(set(all_proxies))
    print(f"\nTotal unique proxies: {len(all_proxies)}")
    return all_proxies


def test_proxy(proxy):
    """Test if a proxy works."""
    try:
        # Determine proxy type
        if proxy.startswith('socks4://') or proxy.startswith('socks5://'):
            proxies = {
                'http': proxy,
                'https': proxy
            }
        else:
            # Assume HTTP proxy
            if not proxy.startswith('http://'):
                proxy = f'http://{proxy}'
            proxies = {
                'http': proxy,
                'https': proxy
            }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
        
        response = requests.get(
            TEST_URL,
            proxies=proxies,
            headers=headers,
            timeout=TEST_TIMEOUT,
            allow_redirects=True
        )
        
        if response.status_code == 200 and len(response.text) > 1000:
            return proxy, True
        
    except Exception:
        pass
    
    return proxy, False


def test_proxies(proxies):
    """Test all proxies concurrently."""
    print(f"\nTesting {len(proxies)} proxies with {MAX_WORKERS} workers...")
    print(f"(This may take a few minutes)\n")
    
    working_proxies = []
    tested = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
        
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy, works = future.result()
            tested += 1
            
            if works:
                working_proxies.append(proxy)
                print(f"✓ [{tested}/{len(proxies)}] Working: {proxy}")
            else:
                if tested % 50 == 0:
                    print(f"  [{tested}/{len(proxies)}] Tested so far, {len(working_proxies)} working...")
    
    print(f"\nTesting complete: {len(working_proxies)}/{len(proxies)} proxies are working")
    return working_proxies


def save_whitelist(proxies):
    """Save working proxies to a timestamped whitelist file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H")
    filename = f"whitelist_{timestamp}.txt"
    
    # Save in tests/proxies directory
    proxies_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests', 'proxies')
    os.makedirs(proxies_dir, exist_ok=True)
    
    filepath = os.path.join(proxies_dir, filename)
    
    with open(filepath, 'w') as f:
        for proxy in sorted(proxies):
            f.write(f"{proxy}\n")
    
    print(f"\nWhitelist saved to: {filepath}")
    return filepath


def main():
    """Main execution."""
    print("=" * 60)
    print("Proxy Whitelist Generator")
    print("=" * 60)
    print()
    
    # Fetch proxies
    proxies = fetch_proxies()
    
    if not proxies:
        print("No proxies fetched. Exiting.")
        return
    
    # Test proxies
    working_proxies = test_proxies(proxies)
    
    if not working_proxies:
        print("\nNo working proxies found!")
        return
    
    # Save whitelist
    filepath = save_whitelist(working_proxies)
    
    print()
    print("=" * 60)
    print(f"Summary: {len(working_proxies)} working proxies saved")
    print("=" * 60)


if __name__ == "__main__":
    main()
