"""
Test all proxies from http.txt sequentially and save working ones.
"""

import requests
import time


def test_proxy(proxy_url, test_timeout=10):
    """Test if a proxy is working."""
    proxies = {
        'http': f'http://{proxy_url}',
        'https': f'http://{proxy_url}',
    }
    
    try:
        # Quick connectivity test with httpbin
        start = time.time()
        resp = requests.get(
            'http://httpbin.org/ip',
            proxies=proxies,
            timeout=test_timeout
        )
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            return True, elapsed
        return False, 0
    except:
        return False, 0


def main():
    print("=" * 70)
    print("TESTING ALL PROXIES FROM http.txt")
    print("=" * 70)
    
    # Load all proxies
    with open('http.txt', 'r') as f:
        all_proxies = [line.strip() for line in f if line.strip()]
    
    print(f"\nTotal proxies to test: {len(all_proxies)}")
    print("Testing sequentially with 10s timeout per proxy...")
    print("This may take a while...\n")
    
    working_proxies = []
    tested = 0
    
    for i, proxy in enumerate(all_proxies, 1):
        tested += 1
        
        # Progress indicator every 50 proxies
        if i % 50 == 0:
            print(f"\nProgress: {i}/{len(all_proxies)} tested, {len(working_proxies)} working")
        
        # Test the proxy
        is_working, response_time = test_proxy(proxy)
        
        if is_working:
            working_proxies.append((proxy, response_time))
            print(f"✓ {i:4d}. {proxy:25} - {response_time:.2f}s")
        else:
            # Show dots for failed proxies (less verbose)
            if i % 50 != 0:
                print(".", end="", flush=True)
    
    print("\n\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\nTested: {tested}")
    print(f"Working: {len(working_proxies)}")
    print(f"Failed: {tested - len(working_proxies)}")
    print(f"Success rate: {len(working_proxies)/tested*100:.1f}%")
    
    if working_proxies:
        # Sort by response time
        working_proxies.sort(key=lambda x: x[1])
        
        print(f"\n{len(working_proxies)} Working proxies (sorted by speed):")
        print("-" * 70)
        for proxy, response_time in working_proxies:
            print(f"{proxy:30} - {response_time:.2f}s")
        
        # Save to file
        output_file = 'http_working.txt'
        with open(output_file, 'w') as f:
            for proxy, _ in working_proxies:
                f.write(f"{proxy}\n")
        
        print(f"\n✓ Saved working proxies to: {output_file}")
        
        # Test the fastest one with Bing
        print("\n" + "=" * 70)
        print("TESTING FASTEST PROXY WITH BING")
        print("=" * 70)
        
        fastest_proxy = working_proxies[0][0]
        print(f"\nTesting: {fastest_proxy}")
        
        test_bing_with_proxy(fastest_proxy)
    else:
        print("\n⚠️  No working proxies found")


def test_bing_with_proxy(proxy_url):
    """Quick test with Bing."""
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
            print("  ✗ CAPTCHA detected (proxy may be blocked by Bing)")
        else:
            tree = lhtml.fromstring(resp.content)
            results = tree.xpath('//li[@class="b_algo"]')
            print(f"  ✓ No CAPTCHA! Found {len(results)} results")
            
            if results:
                print(f"\n  Sample result:")
                link = results[0].xpath('.//h2/a')
                if link:
                    print(f"    {link[0].text_content()[:60]}...")
    except Exception as e:
        print(f"  ✗ Error: {e}")


if __name__ == '__main__':
    start_time = time.time()
    main()
    elapsed = time.time() - start_time
    print(f"\n\nTotal time: {elapsed/60:.1f} minutes")
