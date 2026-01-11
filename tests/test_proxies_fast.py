"""
Test proxies in parallel and save working ones.
Stops after finding 20 working proxies or testing all.
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def test_proxy(proxy_url, test_timeout=8):
    """Test if a proxy is working."""
    proxy = proxy_url.strip()
    
    proxies = {
        'http': f'http://{proxy}',
        'https': f'http://{proxy}',
    }
    
    try:
        start = time.time()
        resp = requests.get(
            'http://httpbin.org/ip',
            proxies=proxies,
            timeout=test_timeout
        )
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            return proxy, True, elapsed
        return proxy, False, 0
    except:
        return proxy, False, 0


def test_bing_with_proxy(proxy_url):
    """Test Bing search with proxy."""
    from lxml import html as lhtml
    
    url = "https://www.bing.com/search?q=test"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    proxies = {
        'http': f'http://{proxy_url}',
        'https': f'http://{proxy_url}',
    }
    
    try:
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        
        has_captcha = 'captcha' in resp.text.lower() or 'robot' in resp.text.lower()
        
        if has_captcha:
            return False, 0
        else:
            tree = lhtml.fromstring(resp.content)
            results = tree.xpath('//li[@class="b_algo"]')
            return True, len(results)
    except:
        return False, 0


def main():
    print("=" * 70)
    print("TESTING PROXIES IN PARALLEL (Fast Mode)")
    print("=" * 70)
    
    # Load all proxies
    with open('http.txt', 'r') as f:
        all_proxies = [line.strip() for line in f if line.strip()]
    
    print(f"\nTotal proxies: {len(all_proxies)}")
    print(f"Testing with 20 parallel workers...")
    print(f"Will stop after finding 20 working proxies\n")
    
    working_proxies = []
    tested = 0
    max_working = 20
    
    start_time = time.time()
    
    # Test in batches with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Submit all tests
        futures = {executor.submit(test_proxy, proxy): proxy for proxy in all_proxies}
        
        for future in as_completed(futures):
            tested += 1
            proxy, is_working, response_time = future.result()
            
            if is_working:
                working_proxies.append((proxy, response_time))
                print(f"✓ {len(working_proxies):2d}. {proxy:30} - {response_time:.2f}s")
                
                # Stop if we have enough
                if len(working_proxies) >= max_working:
                    print(f"\n✓ Found {max_working} working proxies, stopping search...")
                    # Cancel remaining futures
                    for f in futures:
                        f.cancel()
                    break
            
            # Progress update every 100
            if tested % 100 == 0:
                print(f"  ... tested {tested}/{len(all_proxies)}, found {len(working_proxies)} working")
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\nTested: {tested}")
    print(f"Working: {len(working_proxies)}")
    print(f"Time: {elapsed:.1f}s")
    
    if working_proxies:
        # Sort by response time
        working_proxies.sort(key=lambda x: x[1])
        
        # Save to file
        output_file = 'http_working.txt'
        with open(output_file, 'w') as f:
            for proxy, _ in working_proxies:
                f.write(f"{proxy}\n")
        
        print(f"\n✓ Saved {len(working_proxies)} working proxies to: {output_file}")
        
        # Test fastest 5 with Bing
        print("\n" + "=" * 70)
        print("TESTING FASTEST 5 PROXIES WITH BING")
        print("=" * 70)
        
        bing_working = []
        for proxy, speed in working_proxies[:5]:
            print(f"\nTesting: {proxy} ({speed:.2f}s)")
            success, result_count = test_bing_with_proxy(proxy)
            
            if success:
                print(f"  ✓ SUCCESS! No CAPTCHA, {result_count} results found")
                bing_working.append(proxy)
            else:
                print(f"  ✗ CAPTCHA detected or error")
        
        if bing_working:
            print(f"\n🎉 {len(bing_working)} proxy(ies) work with Bing!")
            print("\nBing-compatible proxies:")
            for proxy in bing_working:
                print(f"  - {proxy}")
            
            # Save Bing-working proxies
            with open('http_bing_working.txt', 'w') as f:
                for proxy in bing_working:
                    f.write(f"{proxy}\n")
            print("\n✓ Saved to http_bing_working.txt")
        else:
            print("\n⚠️  None of the fastest proxies work with Bing")
            print("   Bing may be blocking these proxy IPs too")
    else:
        print("\n⚠️  No working proxies found")


if __name__ == '__main__':
    main()
