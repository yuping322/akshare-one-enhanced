# API Contract: get_northbound_flow

## Overview

**API Function**: `get_northbound_flow`

**Purpose**: Get daily northbound capital flow data showing net buying/selling activity from Hong Kong investors into A-share markets.

**Module**: `akshare_one.modules.northbound`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Trading date | `2024-01-15` |
| `northbound_net_buy` | float | yuan | Net buy amount (当日成交净买额) | `1234567890` |
| `northbound_buy_amount` | float | yuan | Total buy amount (买入成交额) | `5234567890` |
| `northbound_sell_amount` | float | yuan | Total sell amount (卖出成交额) | `4000000000` |

### Field Types

- `datetime`: Date in YYYY-MM-DD format
- `float`: Floating-point numeric data
- `yuan`: Chinese Yuan (元) - all amounts in yuan (not 亿元)

## Optional Fields

The following fields MAY be present depending on the data source.

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `market` | string | - | Market type (`sh`, `sz`, `all`) | All responses |
| `northbound_balance` | float | yuan | Daily balance (当日余额) | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `stock_hsgt_hist_em`):
- `日期` → `date`
- `当日成交净买额` → `northbound_net_buy` (converted from 亿元 to 元)
- `买入成交额` → `northbound_buy_amount` (converted from 亿元 to 元)
- `卖出成交额` → `northbound_sell_amount` (converted from 亿元 to 元)
- `当日余额` → `northbound_balance` (converted from 亿元 to 元)

**Field Transformations**:
- All amounts converted from 亿元 (hundred million yuan) to 元 (yuan) by multiplying by 100,000,000
- This ensures consistency with other APIs that use yuan as base unit

## Update Frequency

- **Daily data**: Updated daily after market close (15:00+)
- Historical data available from program start date (2014 for Shanghai, 2016 for Shenzhen)

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `market` | string | no | `all` | Market: `sh` (Shanghai), `sz` (Shenzhen), `all` |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter list |
| `row_filter` | dict | no | None | Row filter configuration |

## Example Usage

```python
from akshare_one import get_northbound_flow

# Basic usage - get all northbound flow data
df = get_northbound_flow()

# Get data for specific date range
df = get_northbound_flow(
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# Get Shanghai market only
df = get_northbound_flow(
    market="sh",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# With column filtering
df = get_northbound_flow(
    columns=['date', 'northbound_net_buy']
)

# Multi-source version
from akshare_one import get_northbound_flow_multi_source
df = get_northbound_flow_multi_source()
```

## Example Response

```python
# Example DataFrame structure
         date  northbound_net_buy  northbound_buy_amount  northbound_sell_amount
0  2024-01-15         1234567890.0          5234567890.0          4000000000.0
1  2024-01-16         -500000000.0          3000000000.0          3500000000.0
```

## Validation Rules

1. **Required Fields**: All minimum fields MUST be present (`date`, `northbound_net_buy`, `northbound_buy_amount`, `northbound_sell_amount`)
2. **Type Validation**:
   - `date`: datetime or string in YYYY-MM-DD format
   - Amount fields: numeric (float)

3. **Value Ranges**:
   - `date`: Valid trading date (non-null)
   - Amounts can be positive (net buy) or negative (net sell)
   - All amounts in yuan (元), typically in billions

4. **Consistency Rules**:
   - `northbound_net_buy` = `northbound_buy_amount` - `northbound_sell_amount`
   - Amounts should be reasonable (typically in the range of billions of yuan)

## Error Handling

- **Empty DataFrame**: Returned when no data available for the specified period
- **Exception Handling**: Network errors and API failures are caught and logged
- **Fallback Behavior**: Multi-source version automatically tries alternative sources

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_northbound_holdings`: Get northbound holdings by stock
- `get_northbound_top_stocks`: Get top stocks by northbound holdings
- `get_northbound_flow_multi_source`: Multi-source version with auto-failover

## Testing

Contract tests for this API are located in:
- `tests/test_api_contract.py::TestNorthboundContract`
- `tests/test_northbound_contract.py`
- `tests/test_api_field_contracts.py::TestNorthboundFlowContract`

Test coverage includes:
- Required field presence
- Field type validation
- Net buy calculation consistency
- Value range validation

## Notes

- Northbound capital = investment from Hong Kong into A-share markets via stock connect
- Shanghai Connect started Nov 2014, Shenzhen Connect started Dec 2016
- Positive net buy indicates capital inflow, negative indicates outflow
- Amounts converted from 亿元 to 元 for consistency with other APIs
- Data reflects daily aggregate, not individual transactions
- Market parameter allows filtering by Shanghai (`sh`) or Shenzhen (`sz`) connect separately