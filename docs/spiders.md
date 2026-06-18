# Spiders

## `bookSpider.py` — `BookspiderSpider`

Crawls book listings and individual book pages.

**Name:** `"bookSpider"`

**Start URL:** `https://librarius.md/ro/books/page/1`

**Pipelines (set via `custom_settings`):**
- `BookscrapePipeline` (priority 300) — data cleaning
- `SaveBookToMySQLPipeline` (priority 400) — MySQL persistence

### Custom Settings

| Setting | Description |
|---|---|
| `BOOKS_MAX_PAGES` | Maximum number of pagination pages to crawl (set via `settings.py`, default: 10). A value of 0 means no limit. |

### `parse(response)`

1. Extracts all book URLs from `div.anyproduct-card a::attr(href)` on the listing page.
2. Follows each URL to `parse_book`.
3. Finds the next page link via `li.page-item.active + li.page-item a::attr(href)`.
4. If `books_max_pages` is set and the next page number exceeds it, pagination stops.

### `parse_book(response)`

Extracts the following fields from a book detail page:

| Field | CSS/XPath Selector |
|---|---|
| `url` | `response.url` |
| `name` | `h1.main-title::text` |
| `img_src` | `div._book__cover img::attr(src)` |
| `stock` | `div.product-book-price__stock ::text` |
| `price` | `#addToCartButton::attr(data-price)` |
| `old_price` | `div.product-book-price__discount del::text` |
| `discount_procent` | `span.discount-badge::text` |
| `properties` | Iterates `div.book-props-item`, extracting key from `div.book-prop-name` and value from `div.book-prop-value` |
| `availability` | Iterates `table.table-striped tbody tr`, extracts shop ID from first cell and stock text from third cell |

Yields a `BookItem` for each book.

---

## `shopSpider.py` — `ShopspiderSpider`

Crawls the points-of-sale page to extract physical store locations.

**Name:** `"shopSpider"`

**Start URL:** `https://librarius.md/ro/points-of-sales`

**Pipelines (set via `custom_settings`):**
- `ShopscrapePipeline` (priority 300) — data cleaning
- `SaveShopToMySQLPipeline` (priority 400) — MySQL persistence

### `parse(response)`

1. Iterates over each `div.shop-item` on the page.
2. Extracts:
   - `id` — from `label a::text`
   - `address` — from first content div, `a[title="address"] ::text`
   - `phone` — from second content div, `a[title="phone"] ::text`
   - `schedule` — from third content div, `small/text()` (returned as a list of strings)
3. Filters out shops whose `id` contains `"online"` (case-insensitive).
4. Yields a `ShopItem` for each valid shop.
