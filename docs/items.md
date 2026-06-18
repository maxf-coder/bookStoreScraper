# Data Models (`items.py`)

Defines Scrapy Item classes that serve as data schemas for scraped content. These items are yielded by spiders and consumed by pipelines.

## `BookItem`

Holds data for a single book extracted from its detail page.

| Field | Type | Description | Source |
|---|---|---|---|
| `id` | `int` | Product code (extracted from `properties["Cod produs"]` by pipeline) | Populated in `BookscrapePipeline` |
| `url` | `str` | Book detail page URL | `response.url` |
| `name` | `str` | Book title | `h1.main-title::text` |
| `img_src` | `str` or `None` | Cover image URL (null for empty placeholder covers) | `div._book__cover img::attr(src)` |
| `stock` | `str` | General stock status | `div.product-book-price__stock ::text` |
| `price` | `float` or `None` | Current price | `#addToCartButton::attr(data-price)` |
| `old_price` | `float` or `None` | Original price before discount | `div.product-book-price__discount del::text` |
| `discount_procent` | `float` or `None` | Discount percentage | `span.discount-badge::text` |
| `properties` | `dict` | Key-value pairs of book attributes (publisher, year, pages, etc.) | `div.book-props-item` rows |
| `availability` | `dict` | Maps shop IDs (numeric) to stock status strings | `table.table-striped` rows |

### Usage

```python
from bookScrape.items import BookItem

book = BookItem()
book['url'] = response.url
book['name'] = response.css('h1.main-title::text').get()
yield book
```

## `ShopItem`

Holds data for a physical store location.

| Field | Type | Description | Source |
|---|---|---|---|
| `id` | `int` | Shop identifier | `label a::text` (numeric part extracted by pipeline) |
| `address` | `str` | Street address | `div[1] a[title="address"] ::text` |
| `phone` | `str` | Contact phone number | `div[2] a[title="phone"] ::text` |
| `schedule` | `str` | Opening hours (comma-joined by pipeline) | `div[3] small/text()` (list → joined in `ShopscrapePipeline`) |

### Usage

```python
from bookScrape.items import ShopItem

shop = ShopItem()
shop["id"] = shopDiv.css("label a::text").get()
yield shop
```
