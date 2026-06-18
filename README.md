# BookStoreScraper

A [Scrapy](https://scrapy.org/)-based web scraper for [librarius.md](https://librarius.md), a Moldovan online bookstore. It extracts book listings and physical store locations, cleans the data, and persists it to a MySQL database. Anti-bot countermeasures are handled via [ScrapeOps](https://scrapeops.io/) (rotating browser headers + proxy fallback).

## Table of Contents

- [Requirements](#requirements)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Data Flow](#data-flow)
- [Logging](#logging)
- [Module Documentation](#module-documentation)

## Requirements

- Python 3.10+
- MySQL server (8.0+ recommended)
- A [ScrapeOps](https://scrapeops.io/) account with an API key

## Setup

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd BookStoreScraper
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the project root with the following variables:

   ```env
   SCRAPEOPS_API_KEY=your_scrapeops_api_key
   DB_HOST=localhost
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=bookscraper
   ```

5. **Ensure your MySQL database exists**

   ```sql
   CREATE DATABASE bookscraper CHARACTER SET utf8mb4;
   ```

## Usage

Run both spiders (books + shops) together:

```bash
python bookScrape/main.py
```

Or run each spider individually via Scrapy:

```bash
scrapy crawl bookSpider
scrapy crawl shopSpider
```

Logs are written to `scraping.log` in the working directory.

## Project Structure

```
BookStoreScraper/
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (not tracked by git)
├── bookScrape/
│   ├── configs.py                  # Logging configuration
│   ├── main.py                     # Application entry point (launches both spiders)
│   ├── scrapy.cfg                  # Scrapy project configuration
│   └── bookScrape/                 # Scrapy app package
│       ├── items.py                # Data models (BookItem, ShopItem)
│       ├── middlewares.py          # Anti-bot middlewares (ScrapeOps)
│       ├── pipelines.py            # Data cleaning + MySQL persistence
│       ├── settings.py             # Scrapy settings
│       └── spiders/
│           ├── bookSpider.py       # Book listing & detail page spider
│           └── shopSpider.py       # Points-of-sale spider
└── docs/
    ├── items.md
    ├── spiders.md
    ├── pipelines.md
    ├── middlewares.md
    └── configuration.md
```

## Database Schema

Three tables are created automatically by the persistence pipelines on first run.

### `books`

| Column | Type | Description |
|---|---|---|
| `id` | `INT NOT NULL` | Product code (from "Cod produs" property), primary key |
| `url` | `TEXT` | Book detail page URL |
| `name` | `VARCHAR(255)` | Book title |
| `img_src` | `TEXT` | Cover image URL (null for empty covers) |
| `stock` | `VARCHAR(20)` | General stock status |
| `price` | `DECIMAL(10,2)` | Current price |
| `old_price` | `DECIMAL(10,2)` | Original price before discount (nullable) |
| `discount_procent` | `DECIMAL(10,2)` | Discount percentage (nullable) |
| `properties` | `JSON` | All additional book attributes (publisher, year, pages, etc.) |

### `shops`

| Column | Type | Description |
|---|---|---|
| `id` | `INT NOT NULL` | Shop identifier, primary key |
| `address` | `VARCHAR(255)` | Shop address |
| `phone` | `VARCHAR(50)` | Phone number |
| `schedule` | `VARCHAR(255)` | Opening hours (comma-separated) |

### `books_shops`

| Column | Type | Description |
|---|---|---|
| `bookId` | `INT NOT NULL` | Foreign key to `books(id)` |
| `shopId` | `INT NOT NULL` | Foreign key to `shops(id)` |
| `stock` | `VARCHAR(20)` | Per-shop stock availability |

Primary key is `(bookId, shopId)`.

## Data Flow

```
HTTP Request ──> Spider ──> Item ──> Cleaning Pipeline ──> MySQL Pipeline ──> Database
                                │
                          ScrapeOps Middlewares
                      (headers + proxy fallback)
```

1. **Spider** sends HTTP requests to librarius.md, receives HTML responses.
2. **Middlewares** automatically rotate browser headers (and retry blocked requests via proxy).
3. **Spider parser** extracts data into a Scrapy `Item` (BookItem or ShopItem).
4. **Cleaning pipeline** (`BookscrapePipeline` / `ShopscrapePipeline`) validates and transforms fields.
5. **MySQL pipeline** (`SaveBookToMySQLPipeline` / `SaveShopToMySQLPipeline`) upserts data into the database.

## Logging

The module-level `scrapingLogger` in `bookScrape/configs.py` writes `INFO`-level and above messages to `scraping.log` with the format:

```
2026-01-15 14:30:00,123 - WARNING - Drop item https://... invalid id
```

Used by pipelines and middlewares to log dropped items, blocked requests, and processing errors.

## Module Documentation

Detailed documentation for each module is available in the `docs/` directory:

- [Data Models (items.py)](docs/items.md)
- [Spiders](docs/spiders.md)
- [Pipelines](docs/pipelines.md)
- [Middlewares](docs/middlewares.md)
- [Configuration](docs/configuration.md)
