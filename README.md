# Capterra Scraper

A Python scraper for collecting software product data from [Capterra](https://www.capterra.com). Discovers categories, paginates product listings, and extracts detailed product information from SSR-rendered pages.

## Features

- Category discovery via the `/categories/` page
- Paginated product URL collection per category
- Threaded product detail extraction
- Proxy and cookie rotation support
- CSV and JSON export with deduplication

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Configuration

Set the following environment variables:

| Variable | Description |
|---|---|
| `CAPTERRA_PROXY_HOST` | Proxy hostname |
| `CAPTERRA_PROXY_PORT` | Proxy port (default: 22225) |
| `CAPTERRA_PROXY_USER` | Proxy username |
| `CAPTERRA_PROXY_PASS` | Proxy password |
| `CAPTERRA_COOKIE_AUTH` | Auth token for cookie API |
| `CAPTERRA_COOKIE` | Pre-set cookie string (optional) |

## Usage

```bash
python -m capterra_scraper --threads 4 --max-workers 8 --output output/
```

Skip category discovery with an existing file:

```bash
python -m capterra_scraper --categories-file output/categories.json
```

## Testing

```bash
pytest
```

## Project Structure

```
capterra_scraper/
├── __init__.py
├── __main__.py          # CLI entry point
├── config.py            # Environment-based configuration
├── runner.py            # Pipeline orchestrator
├── models/
│   └── product.py       # Product and CategoryInfo dataclasses
├── services/
│   ├── http_client.py   # Proxied HTTP client
│   └── cookie_manager.py
├── spiders/
│   ├── category_spider.py
│   └── product_spider.py
└── exporters/
    ├── csv_exporter.py
    └── json_exporter.py
```
