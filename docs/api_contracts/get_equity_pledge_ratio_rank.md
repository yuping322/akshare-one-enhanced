# API Contract: get_equity_pledge_ratio_rank

## Overview

**API Function**: `get_equity_pledge_ratio_rank`

**Purpose**: Get stocks ranked by equity pledge ratio.

**Module**: `akshare_one.modules.pledge`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol | "600000" |
| `name` | string | - | Stock name | "浦发银行" |
| `pledge_ratio` | float | percent | Total pledge ratio | 50.0 |
| `unpledged_ratio` | float | percent | Unpledged ratio | 50.0 |
| `pledge_count` | int | - | Number of pledge events | 10 |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | Yes | - | Query date |
| `top_n` | int | No | 100 | Number of top stocks to return |
| `source` | string | No | "eastmoney" | Data source |

## Related APIs

- `get_equity_pledge`: Get detailed pledge information
