# API Contract: get_goodwill_data

## Overview

**API Function**: `get_goodwill_data`

**Purpose**: Get goodwill (商誉) data for stocks.

**Module**: `akshare_one.modules.goodwill`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol | "600000" |
| `name` | string | - | Stock name | "浦发银行" |
| `report_date` | datetime | - | Report date | "2023-12-31" |
| `goodwill_amount` | float | yuan | Goodwill amount | 100000000 |
| `goodwill_ratio` | float | percent | Goodwill to assets ratio | 5.2 |
| `net_assets` | float | yuan | Net assets | 5000000000 |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | No | None | Stock symbol. If None, returns all stocks |
| `start_date` | string | No | "1970-01-01" | Start date |
| `end_date` | string | No | "2030-12-31" | End date |
| `source` | string | No | "eastmoney" | Data source |

## Related APIs

- `get_goodwill_impairment`: Get goodwill impairment expectations
- `get_goodwill_by_industry`: Get goodwill statistics by industry
