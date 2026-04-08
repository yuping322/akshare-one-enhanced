# API Contract: get_esg_rating

## Overview

**API Function**: `get_esg_rating`

**Purpose**: Get ESG (Environmental, Social, Governance) rating data for stocks.

**Module**: `akshare_one.modules.esg`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol | "600000" |
| `name` | string | - | Stock name | "浦发银行" |
| `esg_score` | float | score | ESG total score | 85.5 |
| `environment_score` | float | score | Environment score | 90.2 |
| `social_score` | float | score | Social score | 80.3 |
| `governance_score` | float | score | Governance score | 86.5 |
| `rating_date` | datetime | - | Rating date | "2024-01-15" |
| `rating_org` | string | - | Rating organization | "华证指数" |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `esg_level` | string | - | ESG rating level (A, B, C) | eastmoney |
| `industry_avg` | float | score | Industry average score | eastmoney |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | No | None | Stock symbol. If None, returns all stocks |
| `start_date` | string | No | "1970-01-01" | Start date |
| `end_date` | string | No | "2030-12-31" | End date |
| `source` | string | No | "eastmoney" | Data source |

## Example Usage

```python
from akshare_one import get_esg_rating

# Get ESG rating for a specific stock
df = get_esg_rating(symbol="600000")

# Get ESG ratings for all stocks
df = get_esg_rating()
```

## Related APIs

- `get_esg_rating_rank`: Get ESG rating rankings by date/industry

## Notes

- ESG scores are typically in 0-100 range
- Different rating organizations may have different scoring methodologies
