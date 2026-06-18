# Pipelines

Four item pipelines process scraped data in two stages: **cleaning** and **MySQL persistence**.

## BookscrapePipeline (priority 300)

Cleans and validates `BookItem` data before storage.

### Transformation steps (in order):

1. **`name`** — stripped of surrounding whitespace.
2. **`img_src`** — relative paths (starting with `/`) are prefixed with `https://librarius.md`. Empty or absent values are set to `None`. The default empty-cover placeholder image is also replaced with `None`.
3. **`stock`** — whitespace-stripped.
4. **`price`, `old_price`, `discount_procent`** — converted from comma-delimited strings to floats via `parse_price()`. Returns `None` on missing or unparseable values.
5. **`properties`** — all keys and values are whitespace-stripped. On failure, the item is dropped and logged.
6. **`id`** — extracted from `properties["Cod produs"]`, which is removed from the properties dict. If missing or non-numeric, the item is dropped and logged.
7. **`availability`** — each key is parsed for a numeric shop ID via regex `\b\d+\b`. Entries with a valid ID and non-empty stock are kept as `{shop_id: stock}`. Invalid entries are logged.

### `parse_price(value)`

Converts a price string to float:

```python
parse_price("150,00")   # → 150.0
parse_price("")         # → None
parse_price("abc")      # → None
```

## SaveBookToMySQLPipeline (priority 400)

Persists cleaned `BookItem` data to MySQL.

### Initialization

- Connects to MySQL using `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` from settings.
- Creates `books` table if it does not exist.
- Creates `books_shops` junction table if it does not exist (references both `books` and `shops`).

### `process_item(item, spider)`

1. **Upserts the book** into `books` via `INSERT ... ON DUPLICATE KEY UPDATE`. This means re-crawling a book updates its existing record.
2. **Upserts availability entries** into `books_shops` via `executemany` with `ON DUPLICATE KEY UPDATE`. Each entry links a book to a shop with a stock status.

### `close_spider(spider)`

Closes the MySQL cursor and connection.

---

## ShopscrapePipeline (priority 300)

Cleans and validates `ShopItem` data.

### Transformation steps:

1. **`id`** — numeric part extracted via regex `\b\d+\b`. If no digits are found, the item is dropped and logged.
2. **`address`, `phone`** — whitespace-stripped.
3. **`schedule`** — a list of text lines is joined into a comma-separated string. On error, it defaults to an empty string and is logged.

---

## SaveShopToMySQLPipeline (priority 400)

Persists cleaned `ShopItem` data to MySQL.

### Initialization

- Connects to MySQL using the same environment variables.
- Creates `shops` table if it does not exist.

### `process_item(item, spider)`

Upserts the shop into `shops` via `INSERT ... ON DUPLICATE KEY UPDATE`.

### `close_spider(spider)`

Closes the MySQL cursor and connection.
