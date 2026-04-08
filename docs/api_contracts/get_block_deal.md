# API Contract: get_block_deal

## Overview

**API Function**: `get_block_deal`

**Purpose**: Get block deal (大宗交易) transaction data.

**Module**: `akshare_one.modules.blockdeal`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Transaction date | `2024-01-15` |
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `price` | float | yuan | Transaction price | `10.50` |
| `volume` | float | shares | Transaction volume | `1000000` |
| `amount` | float | yuan | Transaction amount | `10500000` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `name` | string | - | Stock name | Most sources |
| `buyer_broker` | string | - | Buyer broker name | Most sources |
| `seller_broker` | string | - | Seller broker name | Most sources |
| `premium_rate` | float | percent | Premium/discount rate vs market price | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare block deal API):
- `交易日期` → `date`
- `证券代码` → `symbol`
- `证券简称` → `name`
- `成交价` → `price`
- `成交量` → `volume`
- `成交金额` → `amount`
- `买方营业部` → `buyer_broker`
- `卖方营业部` → `seller_broker`
- `溢价率` → `premium_rate`

**Field Transformations**:
- Date converted to datetime
- Volume in shares
- Amount in yuan

## Update Frequency

- **Daily**: Updated after market close
- Historical block deal data available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | no | None | Stock symbol (if None, returns all) |
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_block_deal

# Get all block deals
df = get_block_deal()

# Get block deals for specific stock
df = get_block_deal(symbol="600000")

# Get block deals in date range
df = get_block_deal(
    start_date="2024-01-01",
    end_date="2024-03-31"
)

# With column filtering
df = get_block_deal(
    symbol="600000",
    columns=['date', 'price', 'volume', 'amount', 'buyer_broker']
)
```

## Example Response

```python
# Example DataFrame structure
         date  symbol     name  price    volume       amount        buyer_broker        seller_broker  premium_rate
0  2024-01-15  600000  浦发银行  10.50  1000000.0  10500000.0  中信证券上海分公司  华泰证券北京分公司          -2.5
```

## Validation Rules

1. **Required Fields**: `date`, `symbol`, `price`, `volume`, `amount`
2. **Type Validation**:
   - `date`: datetime
   - `price`: float, positive
   - `volume`: float, positive
   - `amount`: float, positive
3. **Consistency**: amount ≈ price × volume

## Error Handling

- **Empty DataFrame**: No block deals in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_block_deal_summary`: Get block deal summary statistics

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestBlockDealContract`

## Notes

- Block deals = large off-exchange trades
- Usually involves institutional investors
- Price may differ from market price
- Negative premium_rate = discount to market
- Positive premium_rate = premium to market
- Large block deals may signal major moves
- Track buyer/seller brokers for patterns
- Important for monitoring institutional activity