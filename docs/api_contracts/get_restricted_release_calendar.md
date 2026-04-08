# API Contract: get_restricted_release_calendar

## Overview

**API Function**: `get_restricted_release_calendar`

**Purpose**: Get restricted stock release calendar (aggregated by date).

**Module**: `akshare_one.modules.restricted`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Release date | "2024-03-15" |
| `company_count` | int | - | Number of companies with releases | 10 |
| `total_amount` | float | yuan | Total release amount | 5000000000 |
| `avg_ratio` | float | percent | Average release ratio | 3.5 |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | No | "1970-01-01" | Start date |
| `end_date` | string | No | "2030-12-31" | End date |
| `source` | string | No | "eastmoney" | Data source |

## Related APIs

- `get_restricted_release`: Get detailed release information
