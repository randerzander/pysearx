"""
Browser-based fetching using Playwright for search engines that block simple HTTP requests.
"""

from typing import Optional
from playwright.sync_api import sync_playwright, Browser, Page
import atexit

# Global browser instance (lazy initialized)
_browser: Optional[Browser] = None
_playwright = None


def get_browser() -> Browser:
    """Get or create a shared browser instance."""
    global _browser, _playwright
    
    if _browser is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=True)
        # Clean up on exit
        atexit.register(cleanup_browser)
    
    return _browser


def cleanup_browser():
    """Clean up browser resources."""
    global _browser, _playwright
    
    if _browser is not None:
        _browser.close()
        _browser = None
    
    if _playwright is not None:
        _playwright.stop()
        _playwright = None


def fetch_with_browser(url: str, wait_selector: Optional[str] = None, timeout: int = 10000) -> str:
    """
    Fetch a URL using a headless browser.
    
    Args:
        url: URL to fetch
        wait_selector: Optional CSS selector to wait for before returning
        timeout: Timeout in milliseconds (default 10000)
        
    Returns:
        HTML content of the page
    """
    browser = get_browser()
    page = browser.new_page()
    
    try:
        # Use 'load' instead of 'networkidle' for faster response
        page.goto(url, wait_until='load', timeout=timeout)
        
        # Wait for specific selector if provided
        if wait_selector:
            page.wait_for_selector(wait_selector, timeout=5000)
        else:
            # Default wait for dynamic content
            page.wait_for_timeout(1500)
        
        content = page.content()
        return content
    finally:
        page.close()
