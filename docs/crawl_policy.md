# Crawl Policy

## Principles

- **robots.txt compliance**: Every URL is checked against `robots.txt` before fetching. Disallowed URLs are skipped and logged.
- **Rate limiting**: Minimum 3 seconds between requests per domain (configurable via `DEFAULT_CRAWL_DELAY_SEC` in `config.py`).
- **Caching**: All HTTP responses are cached in `data/cache.db` (SQLite). Cache TTL is 7 days. Cached responses skip network requests entirely.
- **No CAPTCHA bypass**: Do not attempt to bypass CAPTCHA or access member-only areas.
- **User-Agent**: `gyoza-tare-map-bot/0.1`

## Source Priority

1. **APIs** — most stable, structured data
2. **RSS feeds** — less likely to disallow scraping, structured entry list
3. **Static HTML** — standard web pages
4. **Playwright** — JS-heavy pages only when unavoidable (Phase 3)

## Domain Rate Limit Table

| Domain pattern          | Delay (sec) | Notes                       |
|-------------------------|-------------|-----------------------------|
| (default)               | 3.0         | Applies to all domains      |

Override per-domain delays by editing `config.py` when needed.

## Data Source Checklist

Before adding a URL to `seeds.yaml`:
1. Check `robots.txt` at `https://<domain>/robots.txt`
2. Review the site's Terms of Service for scraping restrictions
3. Prefer RSS feeds over full HTML scraping where available
4. Prefer sources that explicitly allow non-commercial research use
