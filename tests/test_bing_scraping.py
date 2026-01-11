"""
Test Bing scraping with BeautifulSoup approach.
Compare current lxml implementation vs BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup
from lxml import html


def test_beautifulsoup_approach():
    """Test Bing scraping using BeautifulSoup."""
    print("=" * 70)
    print("BING SCRAPING TEST - BeautifulSoup Approach")
    print("=" * 70)
    
    query = "python programming"
    url = f"https://www.bing.com/search?q={query}&rdr=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }
    
    print(f"\nQuery: {query}")
    print(f"URL: {url}\n")
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {resp.status_code}")
        print(f"Content Length: {len(resp.text)} bytes\n")
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find results using class b_algo
        results = soup.find_all("li", {"class": "b_algo"})
        
        print(f"Found {len(results)} results using BeautifulSoup\n")
        
        if results:
            for i, result in enumerate(results[:5], 1):
                try:
                    title_elem = result.find("a")
                    title = title_elem.text if title_elem else "N/A"
                    link = title_elem.get("href") if title_elem else "N/A"
                    
                    desc_elem = result.find("div", {"class": "b_caption"})
                    description = desc_elem.text if desc_elem else "N/A"
                    
                    print(f"{i}. {title}")
                    print(f"   URL: {link}")
                    print(f"   Desc: {description[:100]}...")
                    print()
                except Exception as e:
                    print(f"{i}. Error parsing result: {e}")
        else:
            # Debug: show what classes are present
            all_li = soup.find_all("li")
            print(f"Total <li> elements: {len(all_li)}")
            if all_li:
                classes = set()
                for li in all_li[:20]:
                    if li.get('class'):
                        classes.update(li.get('class'))
                print(f"Sample classes found: {list(classes)[:10]}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_lxml_approach():
    """Test Bing scraping using current lxml approach."""
    print("\n" + "=" * 70)
    print("BING SCRAPING TEST - Current lxml Approach")
    print("=" * 70)
    
    query = "python programming"
    url = f"https://www.bing.com/search?q={query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.bing.com/',
    }
    
    print(f"\nQuery: {query}")
    print(f"URL: {url}\n")
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {resp.status_code}")
        print(f"Content Length: {len(resp.content)} bytes\n")
        
        tree = html.fromstring(resp.content)
        
        # Try different selectors
        selectors = [
            '//li[@class="b_algo"]',
            '//li[contains(@class, "b_algo")]',
            '//ol[@id="b_results"]/li',
        ]
        
        for selector in selectors:
            results = tree.xpath(selector)
            print(f"Selector '{selector}': {len(results)} results")
            
            if results:
                print(f"\nShowing first 3 results:\n")
                for i, elem in enumerate(results[:3], 1):
                    try:
                        link_elem = elem.xpath('.//h2/a')
                        if link_elem:
                            title = link_elem[0].text_content().strip()
                            url = link_elem[0].get('href', '')
                            print(f"{i}. {title}")
                            print(f"   URL: {url}")
                        
                        snippet_elem = elem.xpath('.//p[@class="b_lineclamp4 b_algoSlug"]') or \
                                      elem.xpath('.//div[@class="b_caption"]//p') or \
                                      elem.xpath('.//p')
                        
                        if snippet_elem:
                            desc = snippet_elem[0].text_content().strip()
                            print(f"   Desc: {desc[:100]}...")
                        print()
                    except Exception as e:
                        print(f"{i}. Error: {e}")
                
                return len(results) > 0
        
        # If no results, debug
        print("\nNo results found. Debugging...")
        all_li = tree.xpath('//li')
        print(f"Total <li> elements: {len(all_li)}")
        
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_rdr_param():
    """Test with rdr=1 parameter as suggested."""
    print("\n" + "=" * 70)
    print("BING SCRAPING TEST - With rdr=1 Parameter")
    print("=" * 70)
    
    query = "python programming"
    url = f"https://www.bing.com/search?q={query}&rdr=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    print(f"\nQuery: {query}")
    print(f"URL: {url}\n")
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {resp.status_code}")
        
        tree = html.fromstring(resp.content)
        results = tree.xpath('//li[@class="b_algo"]')
        
        print(f"Found {len(results)} results with rdr=1\n")
        
        if results:
            for i, elem in enumerate(results[:3], 1):
                link_elem = elem.xpath('.//h2/a')
                if link_elem:
                    title = link_elem[0].text_content().strip()
                    url = link_elem[0].get('href', '')
                    print(f"{i}. {title}")
                    print(f"   {url}")
                print()
        
        return len(results) > 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == '__main__':
    print("\nTesting different Bing scraping approaches...\n")
    
    bs_success = test_beautifulsoup_approach()
    lxml_success = test_lxml_approach()
    rdr_success = test_with_rdr_param()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"BeautifulSoup approach: {'✓ Success' if bs_success else '✗ Failed'}")
    print(f"Current lxml approach:  {'✓ Success' if lxml_success else '✗ Failed'}")
    print(f"With rdr=1 parameter:   {'✓ Success' if rdr_success else '✗ Failed'}")
    print("=" * 70)
