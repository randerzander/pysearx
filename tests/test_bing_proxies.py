"""
Test Bing search with HTTP proxies from http.txt
"""

import requests
from lxml import html as lhtml
import time


def load_proxies(filename='http.txt', count=5):
    """Load first N proxies from file."""
    proxies = []
    try:
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i >= count:
                    break
                # Remove line number prefix if present
                proxy = line.strip()
                if '.' in proxy:
                    # Remove number prefix like "1.103.102..." -> "103.102..."
                    parts = proxy.split('.')
                    if len(parts) > 4:
                        proxy = '.'.join(parts[1:])
                    proxies.append(proxy)
    except FileNotFoundError:
        print(f"Error: {filename} not found")
    return proxies


def test_bing_with_proxy(proxy_url, query="python programming"):
    """Test Bing search with a specific proxy."""
    url = f"https://www.bing.com/search?q={query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    proxies = {
        'http': f'http://{proxy_url}',
        'https': f'http://{proxy_url}',  # Use HTTP proxy for HTTPS requests
    }
    
    try:
        print(f"\nTesting proxy: {proxy_url}")
        print(f"  URL: {url}")
        
        start = time.time()
        response = requests.get(
            url,
            headers=headers,
            proxies=proxies,
            timeout=15
        )
        elapsed = time.time() - start
        
        print(f"  ✓ Status: {response.status_code}")
        print(f"  ✓ Time: {elapsed:.2f}s")
        print(f"  ✓ Size: {len(response.content)} bytes")
        
        # Check for CAPTCHA
        has_captcha = 'captcha' in response.text.lower() or 'robot' in response.text.lower()
        if has_captcha:
            print(f"  ✗ CAPTCHA detected")
            return False, 0, elapsed
        else:
            print(f"  ✓ No CAPTCHA!")
        
        # Parse results
        tree = lhtml.fromstring(response.content)
        results = tree.xpath('//li[@class="b_algo"]')
        
        if not results:
            results = tree.xpath('//li[contains(@class, "b_algo")]')
        
        print(f"  ✓ Found {len(results)} results")
        
        if results:
            # Show first 3 results
            for i, elem in enumerate(results[:3], 1):
                try:
                    link_elem = elem.xpath('.//h2/a')
                    if link_elem:
                        title = link_elem[0].text_content().strip()
                        result_url = link_elem[0].get('href', '')
                        print(f"    {i}. {title[:60]}...")
                        print(f"       {result_url[:70]}...")
                except Exception as e:
                    print(f"    {i}. Error parsing: {e}")
        
        return True, len(results), elapsed
        
    except requests.exceptions.ProxyError as e:
        print(f"  ✗ Proxy Error: {e}")
        return False, 0, 0
    except requests.exceptions.Timeout:
        print(f"  ✗ Timeout after 15s")
        return False, 0, 0
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ Connection Error: {e}")
        return False, 0, 0
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False, 0, 0


def main():
    print("=" * 70)
    print("BING SEARCH WITH HTTP PROXIES TEST")
    print("=" * 70)
    
    # Load proxies
    proxies = load_proxies('http.txt', count=5)
    
    if not proxies:
        print("No proxies loaded!")
        return
    
    print(f"\nLoaded {len(proxies)} proxies:")
    for i, proxy in enumerate(proxies, 1):
        print(f"  {i}. {proxy}")
    
    print("\n" + "=" * 70)
    print("TESTING EACH PROXY")
    print("=" * 70)
    
    results = []
    for proxy in proxies:
        success, count, elapsed = test_bing_with_proxy(proxy)
        results.append({
            'proxy': proxy,
            'success': success,
            'result_count': count,
            'elapsed': elapsed
        })
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\nSuccessful: {len(successful)}/{len(results)}")
    print(f"Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print("\n✓ Working proxies:")
        for r in successful:
            print(f"  - {r['proxy']}: {r['result_count']} results in {r['elapsed']:.2f}s")
    
    if failed:
        print("\n✗ Failed proxies:")
        for r in failed:
            print(f"  - {r['proxy']}")
    
    print("\n" + "=" * 70)
    
    if successful:
        print(f"\n🎉 SUCCESS! Found {len(successful)} working proxy(ies)")
        print("   Proxies can bypass Bing's IP blocking!")
    else:
        print("\n⚠️  All proxies failed - they may be blocked or invalid")


if __name__ == '__main__':
    main()
