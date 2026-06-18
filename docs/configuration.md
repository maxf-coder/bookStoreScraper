# Configuration

## Environment Variables (`.env`)

The `.env` file must be placed in the project root. It is loaded by `python-dotenv` in `main.py`.

| Variable | Required | Description |
|---|---|---|
| `SCRAPEOPS_API_KEY` | Yes | API key for ScrapeOps header rotation and proxy services |
| `DB_HOST` | Yes | MySQL server hostname (e.g., `localhost`) |
| `DB_USER` | Yes | MySQL username |
| `DB_PASSWORD` | Yes | MySQL password |
| `DB_NAME` | Yes | MySQL database name |

## Scrapy Settings (`settings.py`)

### Concurrency & Throttling

| Setting | Value | Description |
|---|---|---|
| `CONCURRENT_REQUESTS` | `16` | Maximum concurrent requests |
| `CONCURRENT_REQUESTS_PER_DOMAIN` | `2` | Max concurrent requests per domain |
| `DOWNLOAD_DELAY` | `0` | No fixed delay between requests |
| `AUTOTHROTTLE_ENABLED` | `True` | Auto-throttle enabled |
| `AUTOTHROTTLE_START_DELAY` | `1.5` | Initial delay in seconds |
| `AUTOTHROTTLE_MAX_DELAY` | `20` | Maximum delay in seconds |
| `AUTOTHROTTLE_TARGET_CONCURRENCY` | `1.0` | Average requests per second target |

### Retry & Timeout

| Setting | Value | Description |
|---|---|---|
| `RETRY_ENABLED` | `True` | Retry failed requests |
| `RETRY_TIMES` | `2` | Max retries per request |
| `DOWNLOAD_TIMEOUT` | `15` | Request timeout in seconds |

### Middlewares

| Middleware | Priority |
|---|---|
| `ScrapeOpsHeadersMiddleware` | `300` |
| `ScrapeOpsProxyFallbackMiddleware` | `400` |

### ScrapeOps

| Setting | Source | Description |
|---|---|---|
| `SCRAPEOPS_NUM_RESULTS` | `100` | Number of browser headers to fetch from the API |
| `SCRAPEOPS_API_KEY` | `SCRAPEOPS_API_KEY` env var | API key for ScrapeOps services |

### Pagination

| Setting | Default | Description |
|---|---|---|
| `BOOKS_MAX_PAGES` | `10` | Maximum listing pages to crawl (0 = no limit) |

### Database

| Setting | Env Variable | Description |
|---|---|---|
| `DB_HOST` | `DB_HOST` | MySQL host |
| `DB_USER` | `DB_USER` | MySQL user |
| `DB_PASSWORD` | `DB_PASSWORD` | MySQL password |
| `DB_NAME` | `DB_NAME` | MySQL database name |

### Other

| Setting | Value |
|---|---|
| `ROBOTSTXT_OBEY` | `False` |
| `COOKIES_ENABLED` | `False` |
| `FEED_EXPORT_ENCODING` | `utf-8` |
| `LOG_LEVEL` | `'INFO'` |

## `scrapy.cfg`

Standard Scrapy configuration file.

| Key | Value |
|---|---|
| `default` | `bookScrape.settings` |
| `shell` | `ipython` |
| `project` | `bookScrape` |

## Logging (`configs.py`)

A module-level logger writes to `scraping.log` in the working directory.

| Attribute | Value |
|---|---|
| Logger name | `scrapingLogger` |
| File | `scraping.log` |
| Format | `%(asctime)s - %(levelname)s - %(message)s` |
| Level | `INFO` |
