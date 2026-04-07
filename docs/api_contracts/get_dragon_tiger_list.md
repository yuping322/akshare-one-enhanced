# API Contract: get_dragon_tiger_list

## Overview

**API Function**: `get_dragon_tiger_list`

**Purpose**: Get daily dragon tiger list (龙虎榜) transaction details showing stocks with unusual trading activity and the brokers involved.

**Module**: `akshare_one.modules.lhb`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Trading date | `2024-01-15` |
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `浦发银行` |
| `close` | float | yuan | Closing price | `10.80` |
| `pct_change` | float | percent | Price change percentage | `9.98` |
| `turnover` | float | percent | Turnover rate | `15.23` |
| `reason` | string | - | Reason for listing (上榜原因) | `日涨幅偏离值达7%` |

### Field Types

- `datetime`: Date in YYYY-MM-DD format
- `string`: Stock symbol (6-digit), name, and listing reason
- `float`: Numeric data
- `yuan`: Chinese Yuan (元) - price unit
- `percent`: Percentage value

## Optional Fields

The following fields MAY be present depending on the data source.

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `buy_amount` | float | yuan | Total buy amount from listed brokers | Most responses |
| `sell_amount` | float | yuan | Total sell amount from listed brokers | Most responses |
| `net_amount` | float | yuan | Net buy/sell amount | Most responses |
| `broker_buy` | string | - | Buying broker name | Detailed records |
| `broker_buy_amount` | float | yuan | Buy amount by specific broker | Detailed records |
| `broker_sell` | string | - | Selling broker name | Detailed records |
| `broker_sell_amount` | float | yuan | Sell amount by specific broker | Detailed records |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `stock_lhb_detail_em`):
- `日期` → `date`
- `股票代码` → `symbol`
- `股票名称` → `name`
- `收盘价` → `close`
- `涨跌幅` → `pct_change`
- `换手率` → `turnover`
- `上榜原因` → `reason`
- `买入金额` → `buy_amount` (aggregate)
- `卖出金额` → `sell_amount` (aggregate)
- `买入营业部` → `broker_buy`
- `买入金额-营业部` → `broker_buy_amount`
- `卖出营业部` → `broker_sell`
- `卖出金额-营业部` → `broker_sell_amount`

**Field Transformations**:
- All amounts in yuan (元)
- Percentages as numeric values
- Symbol standardized to 6-digit format

## Update Frequency

- **Daily data**: Updated daily after market close
- Stocks listed based on specific criteria (price deviation, high turnover, etc.)
- Historical data available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | no | None | Query date (YYYY-MM-DD). If None, returns latest |
| `symbol` | string | no | None | Stock symbol. If None, returns all stocks for date |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter list |
| `row_filter` | dict | no | None | Row filter configuration |

## Example Usage

```python
from akshare_one import get_dragon_tiger_list

# Basic usage - get latest dragon tiger list
df = get_dragon_tiger_list()

# Get list for specific date
df = get_dragon_tiger_list(date="2024-01-15")

# Get list for specific stock
df = get_dragon_tiger_list(
    date="2024-01-15",
    symbol="600000"
)

# With column filtering
df = get_dragon_tiger_list(
    columns=['date', 'symbol', 'name', 'pct_change', 'reason']
)

# Multi-source version
from akshare_one import get_dragon_tiger_list_multi_source
df = get_dragon_tiger_list_multi_source(date="2024-01-15")
```

## Example Response

```python
# Example DataFrame structure (summary level)
         date  symbol     name   close  pct_change  turnover           reason
0  2024-01-15  600000   浦发银行   10.80        9.98     15.23     日涨幅偏离值达7%
1  2024-01-15  000001   平安银行   12.30        8.50     12.45     日涨幅偏离值达7%

# Example DataFrame structure (detailed broker level)
         date  symbol     name  broker_buy  broker_buy_amount  broker_sell  broker_sell_amount
0  2024-01-15  600000   浦发银行  中信证券北京总部      50000000.0      华泰证券上海分公司      30000000.0
```

## Validation Rules

1. **Required Fields**: All minimum fields MUST be present (`date`, `symbol`, `name`, `close`, `pct_change`, `turnover`, `reason`)
2. **Type Validation**:
   - `date`: datetime or string in YYYY-MM-DD format
   - `symbol`: string, 6-digit format
   - Price/amounts: numeric (float)
   - Percentages: numeric (float)

3. **Value Ranges**:
   - Close price > 0
   - pct_change can be positive or negative (typically stocks listed for large changes)
   - Turnover rate > 0 (typically high turnover stocks)
   - Amounts can be positive or negative

4. **Listing Criteria**:
   - Stocks listed for: price deviation ≥7%, turnover ≥20%, or other unusual activity
   - Only stocks meeting listing criteria appear on dragon tiger list

## Error Handling

- **Empty DataFrame**: Returned when no stocks listed on specified date or invalid parameters
- **Exception Handling**: Network errors and API failures are caught and logged
- **Fallback Behavior**: Multi-source version automatically tries alternative sources

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_dragon_tiger_summary`: Get aggregated dragon tiger statistics
- `get_dragon_tiger_broker_stats`: Get broker statistics and rankings
- `get_dragon_tiger_list_multi_source`: Multi-source version

## Testing

Contract tests for this API are located in:
- `tests/test_api_field_contracts.py::TestDragonTigerContract`

Test coverage includes:
- Required field presence
- Field type validation
- Value range validation
- Reason field format validation

## Notes

- Dragon tiger list shows stocks with unusual trading activity requiring disclosure
- Common listing reasons: 日涨幅偏离值达7%, 日跌幅偏离值达7%, 日换手率达20%, etc.
- Brokers (营业部) are trading departments of securities firms
- Data helps track institutional trading activity
- Not all stocks appear daily - only those meeting listing criteria
- Detailed records may show multiple brokers per stock