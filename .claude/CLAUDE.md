# PChome 24h Tracking List Price Follower - Agent Maintenance Guide

## Project Overview

A Python CLI tool for tracking product prices on PChome 24h shopping website. Sends Slack and/or Telegram notifications when tracked products reach historical low prices.

## Quick Commands

```bash
make init          # Initialize project (install dependencies)
make run           # Run the tracker
make lint          # Check code style
make lint-fix      # Auto-fix code style issues
make ty            # Run type checking
make docker-build  # Build Docker image
make docker-run    # Run in container
```

## Tech Stack

- **Language**: Python 3.13
- **Package Manager**: uv (not pip)
- **Linter**: ruff
- **Type Checker**: ty (by Astral)
- **HTTP Client**: httpx
- **Database**: SQLite
- **Container**: Docker/Podman

## Project Structure

```
src/
├── main.py              # CLI entry point, main business logic
├── api.py               # PChome API client
├── db.py                # SQLite database operations
├── slack_notifier.py    # Slack notification sender
├── telegram_notifier.py # Telegram notification sender
└── config.py            # Environment variable loader
```

## Key API Documentation

### PChome Tracking List API

```
GET https://ecvip.pchome.com.tw/fsapi/member/products/trace/list
```
- Requires `ECWEBSESS` cookie for authentication
- Returns all products in user's tracking list

### PChome Price API (Button API)

```
GET https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id={productId-000}&fields=Id,Price
```
- No cookie required
- Returns product price information including promotional prices

**Important**: Use `Price.Low` for promotional price. If null, fall back to `Price.P` (regular online price).

## Price Fields Explanation

```json
{
  "Price": {
    "M": 17600,    // Market price (MSRP)
    "P": 15800,    // Online price (regular price)
    "Low": 13904   // Promotional price (may be null)
  }
}
```

Selection logic (implemented in `api.py`):
```python
current_price = promo_price if promo_price else regular_price
```

## Database Schema

- `products`: Tracked products (id, name, created_at, updated_at)
- `price_history`: Price history records (product_id, price, recorded_at)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PCHOME_ECWEBSESS` | ✅ | PChome Session Cookie |
| `SLACK_WEBHOOK_URL` | ❌ | Slack Webhook (no notification if not set) |
| `TELEGRAM_BOT_TOKEN` | ❌ | Telegram Bot Token (both required for Telegram) |
| `TELEGRAM_CHAT_ID` | ❌ | Telegram Chat ID (both required for Telegram) |

## Common Maintenance Tasks

### 1. Update Dependencies

```bash
uv add <package>           # Add dependency
uv add --dev <package>     # Add dev dependency
uv sync                    # Sync dependencies
```

### 2. Handle API Changes

If PChome API changes, modify `src/api.py`:
- `TRACE_LIST_URL`: Tracking list API endpoint
- `BUTTON_API_URL`: Price API endpoint
- `get_tracking_list()`: Parse tracking list response
- `get_prices()`: Parse price response

### 3. Cookie Expiration

When user's `ECWEBSESS` cookie expires, 403 error occurs. Refer to `docs/COOKIE_GUIDE.md` for obtaining a new cookie.

### 4. Docker Related

- Dockerfile uses multi-stage build, image size ~149 MB
- Requires mounting `.env` and `db/` directory at runtime

## Code Style

- Use ruff for linting and formatting
- Line length limit: 100 characters
- Target Python version: 3.13
- Comments in English

## Test Run

```bash
# Local run
make run

# Docker run
make docker-build && make docker-run
```

## Important Notes

1. **DO NOT** directly modify `db/prices.db`, it's auto-generated
2. **DO NOT** commit `.env` to version control
3. After modifying API-related code, always test to ensure prices are fetched correctly
4. Price API product IDs require `-000` suffix
