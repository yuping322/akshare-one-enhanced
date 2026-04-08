# API Contract: get_goodwill_by_industry

## Overview

**API Function**: `get_goodwill_by_industry`

**Purpose**: Get goodwill statistics by industry.

**Module**: `akshare_one.modules.goodwill`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `industry` | string | - | Industry name | "传媒" |
| `company_count` | int | - | Number of companies with goodwill | 50 |
| `total_goodwill` | float | yuan | Total goodwill in industry | 10000000000 |
| `avg_goodwill_ratio` | float | percent | Average goodwill ratio | 10.5 |
| `total_impairment` | float | yuan | Total impairment | 2000000000 |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | No | None | Query date |
| `source` | string | No | "eastmoney" | Data source |

## Related APIs

- `get_goodwill_data`: Get individual stock goodwill data
- `get_goodwill_impairment`: Get impairment expectations
