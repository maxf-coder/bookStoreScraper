# Middlewares

Two downloader middlewares provide anti-bot countermeasures via ScrapeOps.

## ScrapeOpsHeadersMiddleware (priority 300)

Assigns random real browser headers to every outgoing request, making the scraper appear as different browsers/devices.

### Initialization

1. Reads `SCRAPEOPS_API_KEY` and `SCRAPEOPS_NUM_RESULTS` from settings.
2. Calls the ScrapeOps Browser Headers API at `https://headers.scrapeops.io/v1/browser-headers`.
3. Stores the returned header pool (an array of header dictionaries, each containing `User-Agent`, `Accept`, `Accept-Language`, `Accept-Encoding`, etc.).

Raises `RuntimeError` if the API key is missing, the API call fails, or returns an empty list.

### `process_request(request, spider)`

Picks a random header set from the pool and assigns all its key-value pairs to `request.headers`.

```python
# Example of what gets assigned:
request.headers['User-Agent'] = 'Mozilla/5.0 ...'
request.headers['Accept'] = 'text/html,application/xhtml+xml...'
```

---

## ScrapeOpsProxyFallbackMiddleware (priority 400)

Handles blocked requests by retrying them through the ScrapeOps proxy.

### `process_response(request, response, spider)`

1. If the response status is **not** `403` or `429`, returns the original response unchanged.
2. If blocked, logs a warning and asynchronously re-fetches the URL through:
   ```
   https://proxy.scrapeops.io/v1/?api_key={key}&url={url}
   ```
3. Uses `treq` (Twisted-based async HTTP client) for non-blocking proxy requests.
4. On success, returns a new `HtmlResponse` with the proxy content.
5. On failure, logs a warning and falls back to the original blocked response.

### Dependencies

- `treq` — Twisted HTTP client (listed in `requirements.txt`)
- `twisted` — for deferred/async callback handling
