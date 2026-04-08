# API Contract: get_index_valuation

## Overview

**API Function**: `get_index_valuation`

**Purpose**: Get valuation metrics (PE, PB) for market indices from JQ compatibility layer.

**Module**: `akshare_one.jq_compat.valuation`

**Data Sources**: `legu`, `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | Trading date | `2024-01-15` |
| `index_code` | string | - | Index code | `000300` |
| `pe` | float | ratio | Price-to-Earnings ratio | `12.5` |
| `pb` | float | ratio | Price-to-Book ratio | `1.35` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `index_name` | string | - | Index name | Some sources |
| `pe_ttm` | float | ratio | PE (TTM) | Some sources |
| `pe_percentile` | float | percent | PE percentile in history | Some sources |
| `pb_percentile` | float | percent | PB percentile in history | Some sources |

## Data Source Mapping

### Source: `legu`

**Original Fields** (from akshare `stock_a_pe_and_pb_em`):
- `日期` → `date`
- `市盈率` → `pe`
- `市净率` → `pb`

**Field Transformations**:
- Index code added from parameter
- Percentile calculated if historical data available

## Update Frequency

- **Daily**: Updated after market close
- Historical data spans multiple years

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `index_code` | string | yes | - | Index code (e.g., '000300', '000001') |
| `source` | string | no | `legu` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_index_valuation

# Get valuation for CSI 300 index
df = get_index_valuation(index_code="000300")

# Get valuation for SSE Composite
df = get_index_valuation(index_code="000001")

# With column filtering
df = get_index_valuation(
    index_code="000300",
    columns=['date', 'pe', 'pb']
)
```

## Example Response

```python
# Example DataFrame structure
         date index_code     pe     pb index_name
0  2024-01-15    000300   12.50   1.35   沪深300
1  2024-01-16    000300   12.45   1.34   沪深300
```

## Validation Rules

1. **Required Fields**: `date`, `index_code`, `pe`, `pb`
2. **Type Validation**:
   - `pe`, `pb`: float, positive
3. **Value Ranges**:
   - PE typically 5-100 for indices
   - PB typically 0.5-10 for indices

## Error Handling

- **Empty DataFrame**: Invalid index code
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_stock_valuation`: Get individual stock valuation
- `get_market_valuation`: Get market-wide valuation metrics

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestValuationContract`

## Notes

- Useful for market-level valuation analysis
- Compare with historical percentiles for timing
- JQ compatibility function for JoinQuant users