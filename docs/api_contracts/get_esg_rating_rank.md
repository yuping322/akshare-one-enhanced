# API Contract: get_esg_rating_rank

## Overview

**API Function**: `get_esg_rating_rank`

**Purpose**: Get ESG rating rankings for stocks.

**Module**: `akshare_one.modules.esg`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol | "600000" |
| `name` | string | - | Stock name | "浦发银行" |
| `esg_score` | float | score | ESG score | 85.5 |
| `rank` | int | - | Rank position | 1 |
| `industry` | string | - | Industry | "银行" |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | No | None | Query date. If None, returns latest |
| `industry` | string | No | None | Industry filter |
| `top_n` | int | No | 100 | Number of top stocks to return |
| `source` | string | No | "eastmoney" | Data source |

## Example Usage

```python
from akshare_one import get_esg_rating_rank

# Get latest ESG ranking (top 100)
df = get_esg_rating_rank()

# Get ESG ranking for a specific date
df = get_esg_rating_rank(date="2024-01-01", top_n=50)

# Get ESG ranking for a specific industry
df = get_esg_rating_rank(industry="银行")
```

## Related APIs

- `get_esg_rating`: Get detailed ESG ratings for stocks
