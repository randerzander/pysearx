# Search Engine Performance Summary

Last updated: 2026-01-10

## Working Engines (Returning Results)

### Excellent Performance
1. **Brave Search** 🏆
   - Average: 0.47s
   - Results: 10/query
   - Success: 100%
   - Method: HTTP requests with headers

2. **Yahoo Search**
   - Average: 0.81s
   - Results: 7/query
   - Success: 100%
   - Method: HTTP requests with headers

### Good Performance
3. **Mojeek**
   - Average: 1.43s
   - Results: 10/query
   - Success: 100%
   - Method: HTTP requests with headers

4. **Search360** (Chinese)
   - Average: 2.60s
   - Results: 7-8/query
   - Success: 100%
   - Method: HTTP requests with headers

### Intermittent
5. **Bing**
   - Average: 1.96s
   - Results: 1/query (10% success rate)
   - Method: Playwright (inconsistent results)

## Not Working (0 Results / Blocked)

### Bot Detection / Blocking
- **Google** (2.69s avg) - Blocked even with Playwright
- **DuckDuckGo** (10s+ timeouts) - Blocked with Playwright
- **Startpage** (1.93s avg) - Blocked with Playwright
- **Qwant** (3.53s avg) - Blocked even with Playwright
- **Swisscows** (2.83s avg) - Blocked even with Playwright
- **Yandex** (4.77s avg) - Blocked even with Playwright
- **Metager** (0.59s avg) - Returns 0 results

### API Blocked
- **Yep** - 403 Forbidden errors from API
- **Searx** - 403 Forbidden from searx.be instance

## Recommendations

For reliable automated search:
1. **Primary**: Use Brave Search (fastest, most reliable)
2. **Secondary**: Use Yahoo or Mojeek as fallbacks
3. **Chinese content**: Use Search360

Major search engines (Google, Bing, DuckDuckGo) have strong anti-bot measures that are difficult to bypass even with browser automation.

## Technical Notes

- **HTTP + Headers**: Brave, Yahoo, Mojeek, Search360 work with simple HTTP requests and realistic headers
- **Playwright Support**: Added for Google, Bing, DDG, Startpage, Qwant, Swisscows, Yandex but mostly ineffective due to sophisticated bot detection
- **Performance Impact**: Playwright adds ~2-10s overhead per query and still fails for most engines
