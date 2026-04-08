# API Contract: get_fund_manager_info

## Overview

**API Function**: `get_fund_manager_info`

**Purpose**: Get fund manager information for ETFs.

**Module**: `akshare_one.modules.etf`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `fund_code` | string | - | Fund code | "510300" |
| `fund_name` | string | - | Fund name | "300ETF" |
| `manager` | string | - | Fund manager name | "基金经理A" |
| `management_company` | string | - | Management company | "华泰柏瑞" |
| `management_fee` | float | percent | Management fee | 0.5 |
| `inception_date` | datetime | - | Fund inception date | "2012-05-28" |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `fund_code` | string | Yes | - | Fund code |
| `source` | string | No | "eastmoney" | Data source |

## Related APIs

- `get_etf_list`: Get ETF list
- `get_fund_rating_data`: Get fund rating data
