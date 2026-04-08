# API Contract: get_equity_pledge

## Overview

**API Function**: `get_equity_pledge`

**Purpose**: Get equity pledge (股权质押) data.

**Module**: `akshare_one.modules.pledge`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol | "600000" |
| `pledgor` | string | - | Pledgor (质押方) | "股东A" |
| `pledgee` | string | - | Pledgee (质权人) | "银行B" |
| `pledge_date` | datetime | - | Pledge date | "2024-01-15" |
| `pledge_amount` | float | shares | Number of pledged shares | 10000000 |
| `pledge_ratio` | float | percent | Pledge ratio | 5.0 |
| `release_date` | datetime | - | Release date (解押日期) | None |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | No | None | Stock symbol. If None, returns all stocks |
| `start_date` | string | No | "1970-01-01" | Start date |
| `end_date` | string | No | "2030-12-31" | End date |
| `source` | string | No | "eastmoney" | Data source |

## Related APIs

- `get_equity_pledge_ratio_rank`: Get stocks ranked by pledge ratio
