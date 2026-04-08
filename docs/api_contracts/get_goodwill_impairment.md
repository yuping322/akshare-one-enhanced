# API Contract: get_goodwill_impairment

## Overview

**API Function**: `get_goodwill_impairment`

**Purpose**: Get goodwill impairment expectations (商誉减值预期).

**Module**: `akshare_one.modules.goodwill`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol | "600000" |
| `name` | string | - | Stock name | "浦发银行" |
| `impairment_amount` | float | yuan | Expected impairment amount | 50000000 |
| `impairment_ratio` | float | percent | Impairment ratio | 50.0 |
| `goodwill_amount` | float | yuan | Goodwill amount | 100000000 |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | No | None | Query date |
| `source` | string | No | "eastmoney" | Data source |

## Related APIs

- `get_goodwill_data`: Get goodwill balance data
- `get_goodwill_by_industry`: Get industry statistics
