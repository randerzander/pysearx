#!/usr/bin/env python3
"""
Script to add rate limit backoff to all search engines.
"""

import re
from pathlib import Path

ENGINES_DIR = Path('pysearx/engines')

# Engines to update (excluding searx.py and searxng.py which have different logic)
ENGINES = [
    'google', 'bing', 'startpage', 'qwant', 'mojeek',
    'yahoo', 'yep', 'swisscows', 'metager', 'search360', 'yandex'
]


def update_engine(engine_name):
    """Update a single engine file with rate limit backoff."""
    filepath = ENGINES_DIR / f'{engine_name}.py'
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Skip if already updated
    if '_check_rate_limit()' in content and '_handle_rate_limit()' in content:
        print(f"✓ {engine_name} - already updated")
        return
    
    # 1. Update imports - add RateLimitMixin
    content = content.replace(
        'from ..base import SearchEngine, DEFAULT_USER_AGENT, DEFAULT_HEADERS',
        'from ..base import SearchEngine, RateLimitMixin, DEFAULT_USER_AGENT, DEFAULT_HEADERS'
    )
    
    # 2. Update class definition
    class_pattern = rf'class {engine_name.capitalize()}Engine\(SearchEngine\):'
    class_replacement = rf'class {engine_name.capitalize()}Engine(RateLimitMixin, SearchEngine):'
    content = re.sub(class_pattern, class_replacement, content, flags=re.IGNORECASE)
    
    # 3. Add RateLimitMixin.__init__() call
    # Find __init__ method and add the call right after def __init__(self):
    init_pattern = r'(def __init__\(self\):\n)'
    init_replacement = r'\1        RateLimitMixin.__init__(self)\n'
    content = re.sub(init_pattern, init_replacement, content)
    
    # 4. Add rate limit check in search method
    # Find search method docstring end and add check after it
    search_pattern = r'(def search\(self, query: str.*?\n\s+""".*?""")\n(\s+)'
    
    def add_rate_check(match):
        indent = match.group(2)
        return (match.group(1) + '\n' + 
                indent + '# Check if we\'re currently rate limited\n' +
                indent + 'self._check_rate_limit()\n' +
                indent + '\n' + indent)
    
    content = re.sub(search_pattern, add_rate_check, content, flags=re.DOTALL, count=1)
    
    # 5. Update exception handling for rate limits
    except_pattern = (r'except requests\.RequestException as e:\s*\n'
                     r'\s*# Network or HTTP errors\s*\n'
                     r'\s*raise Exception')
    
    except_replacement = '''except requests.RequestException as e:
            error_str = str(e)
            # Check for rate limit
            if self._is_rate_limit_error(error_str):
                self._handle_rate_limit()
            raise Exception'''
    
    content = re.sub(except_pattern, except_replacement, content)
    
    # Write back
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✓ {engine_name} - updated")


def main():
    print("Updating search engines with rate limit backoff...\n")
    
    for engine in ENGINES:
        try:
            update_engine(engine)
        except Exception as e:
            print(f"✗ {engine} - error: {e}")
    
    print("\nDone!")


if __name__ == '__main__':
    main()
