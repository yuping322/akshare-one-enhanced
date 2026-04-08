# API Contract: get_restricted_release

## Overview

**API Function**: `get_restricted_release`

**Purpose**: Get restricted stock release (限售解禁) data.

**Module**: `akshare_one.modules.restricted`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol | "600000" |
| `name` | string | - | Stock name | "浦发银行" |
| `release_date` | datetime | - | Release date | "2024-03-15" |
| `release_amount` | float | shares | Number of shares to release | 10000000 |
| `release_ratio` | float | percent | Release ratio to total shares | 5.0 |
| `holder_type` | string | - | Holder type (首发, 定增, etc.) | "定增" |
| `current_price` | float | yuan | Current price | 10.5 |
| `market_cap` | float | yuan | Market cap | 50000000000 |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | No | None | Stock symbol. If None, returns all stocks |
| `start_date` | string | No | "1970-01-01" | Start date |
| `end_date` | string | No | "2030-12-31" | End date |
| `source` | string | No | "eastmoney" | Data source |

## Related APIs

- `get_restricted_release_calendar`: Get release calendar by date
