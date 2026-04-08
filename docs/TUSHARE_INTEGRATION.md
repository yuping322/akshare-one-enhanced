# Tushare Pro Integration

AKShare One now supports Tushare Pro as an additional data source, providing professional-grade financial data from the Tushare Pro platform.

## Features

Tushare Pro integration provides:
- Financial data (balance sheet, income statement, cash flow, financial metrics)
- Historical market data (daily, weekly, monthly prices)
- Stock basic information
- Trade calendar
- Price adjustment factors (qfq/hfq)

## Installation

Install with Tushare support:

```bash
pip install akshare-one[tushare]
```

Or install Tushare separately:

```bash
pip install tushare>=1.4.0
```

## Configuration

### Get Your API Key

1. Visit [Tushare Pro](https://tushare.pro)
2. Register and login
3. Get your API token from the dashboard

### Set API Key

**Method 1: Environment Variable**

```bash
export TUSHARE_API_KEY="your_api_key_here"
```

**Method 2: Python Code**

```python
from akshare_one.tushare_config import set_tushare_api_key

set_tushare_api_key("your_api_key_here")
```

**Method 3: Configuration File (recommended for production)**

Create `.env` file:
```
TUSHARE_API_KEY=your_api_key_here
```

## Usage Examples

### Financial Data

```python
from akshare_one.tushare_config import set_tushare_api_key
from akshare_one.modules.financial import FinancialDataFactory

# Set API key
set_tushare_api_key("your_api_key")

# Get balance sheet from Tushare
provider = FinancialDataFactory.get_provider("tushare", symbol="600000")
balance_df = provider.get_balance_sheet()

# Get income statement
income_df = provider.get_income_statement()

# Get cash flow
cashflow_df = provider.get_cash_flow()

# Get financial metrics
metrics_df = provider.get_financial_metrics()
```

### Historical Market Data

```python
from akshare_one.modules.historical import HistoricalDataFactory

# Get daily price data
provider = HistoricalDataFactory.get_provider(
    "tushare",
    symbol="600000",
    interval="day",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

df = provider.get_hist_data()

# Get with price adjustment (qfq/hfq)
provider_adj = HistoricalDataFactory.get_provider(
    "tushare",
    symbol="600000",
    interval="day",
    start_date="2024-01-01",
    end_date="2024-01-31",
    adjust="hfq"  # or "qfq" for forward adjustment
)

df_adj = provider_adj.get_hist_data()
```

### Multi-Source Routing

Use Tushare alongside other data sources:

```python
from akshare_one.modules.financial import FinancialDataFactory

# Try Tushare first, fallback to other sources if needed
router = FinancialDataFactory.create_router(
    sources=["tushare", "sina", "eastmoney"],
    symbol="600000"
)

# Will automatically try sources in order
result_df = router.execute("get_balance_sheet")
```

## Symbol Format

Tushare uses a different symbol format (ts_code):
- Shanghai stocks: `600000.SH` (6-digit code + `.SH`)
- Shenzhen stocks: `000001.SZ` (6-digit code + `.SZ`)
- Beijing stocks: `430001.BJ` (6-digit code + `.BJ`)

AKShare One automatically converts standard 6-digit symbols to Tushare format:
- `600000` → `600000.SH`
- `000001` → `000001.SZ`
- `430001` → `430001.BJ`

You can also provide the full ts_code directly:
```python
provider = FinancialDataFactory.get_provider("tushare", symbol="600000.SH")
```

## Available Modules

Currently, Tushare integration supports:

| Module | Factory | Methods |
|--------|---------|---------|
| Financial | `FinancialDataFactory` | `get_balance_sheet`, `get_income_statement`, `get_cash_flow`, `get_financial_metrics` |
| Historical | `HistoricalDataFactory` | `get_hist_data` (daily/weekly/monthly) |

## API Quotas

Tushare Pro has different quota levels based on your membership:
- **Free**: Basic APIs with limited daily calls
- **Paid**: More APIs and higher quotas

Check [Tushare Pro Documentation](https://tushare.pro/document/2) for:
- API quota details
- Permission requirements for each API
- Membership benefits

## Error Handling

```python
from akshare_one.modules.exceptions import DataSourceUnavailableError, RateLimitError

try:
    provider = FinancialDataFactory.get_provider("tushare", symbol="600000")
    df = provider.get_balance_sheet()
except DataSourceUnavailableError as e:
    print(f"Data source unavailable: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
```

## Testing

Run integration tests:

```bash
# Set your API key
export TUSHARE_API_KEY="your_api_key"

# Run tests
pytest tests/test_tushare_integration.py -v -s -m integration
```

## Example Script

See `examples/tushare_example.py` for a complete working example.

## Comparison with Other Sources

| Feature | Tushare | AKShare | Sina | EastMoney |
|---------|---------|---------|------|-----------|
| Financial Data | ✅ Full | ✅ Basic | ✅ Basic | ✅ Basic |
| Historical Data | ✅ Full | ✅ Full | ✅ Limited | ✅ Limited |
| Price Adjustment | ✅ Built-in | ✅ Built-in | ❌ | ❌ |
| Data Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| API Stability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Free Tier | Limited | Unlimited | Unlimited | Unlimited |

## Contributing

To add more Tushare APIs:

1. Add method in `tushare_client.py`
2. Create/update provider in corresponding module
3. Register provider in factory
4. Add tests

## References

- [Tushare Pro Documentation](https://tushare.pro/document/2)
- [Tushare Pro API List](https://tushare.pro/document/2?doc_id=25)
- [AKShare One Documentation](https://zwldarren.github.io/akshare-one/)