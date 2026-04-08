# API Contract: get_fund_rating_data

## Overview

**API Function**: `get_fund_rating_data`

**Purpose**: Get fund rating data for ETFs.

**Module**: `akshare_one.modules.etf`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `fund_code` | string | - | Fund code | "510300" |
| `fund_name` | string | - | Fund name | "300ETF" |
| `rating_org` | string | - | Rating organization | "晨星" |
| `rating` | string | - | Rating level | "5星" |
| `rating_date` | datetime | - | Rating date | "2024-01-15" |
| `return_1y` | float | percent | 1-year return | 15.5 |
| `return_3y` | float | percent | 3-year return | 45.2 |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `fund_code` | string | Yes | - | Fund code |
| `source` | string | No | "eastmoney" | Data source |

## Related APIs

- `get_fund_manager_info`: Get fund manager information
- `get_etf_list`: Get ETF list
