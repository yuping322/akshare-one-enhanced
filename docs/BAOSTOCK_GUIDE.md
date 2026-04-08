# Baostock Data Source Integration

This document describes how to use Baostock as a data source in akshare-one.

## Overview

Baostock is a free financial data platform that provides historical market data for Chinese A-share stocks. It offers:

- Daily, weekly, and monthly historical data
- Price adjustment support (qfq/hfq)
- Free access without API key requirement
- Reliable and stable data server

## Installation

Install the baostock optional dependency:

```bash
pip install akshare-one[baostock]
```

Or install baostock directly:

```bash
pip install baostock
```

## Usage

### Basic Usage

```python
from akshare_one.modules.historical import HistoricalDataFactory

# Create provider instance
provider = HistoricalDataFactory.get_provider(
    "baostock",
    symbol="sh.600000",  # Baostock format: sh/sz + symbol
    interval="day",
    start_date="2024-01-01",
    end_date="2024-01-10"
)

# Fetch historical data
df = provider.get_hist_data()
print(df)
```

### Symbol Format

Baostock uses a specific symbol format: `exchange.symbol`

- Shanghai Stock Exchange: `sh.600000`, `sh.601398`, etc.
- Shenzhen Stock Exchange: `sz.000001`, `sz.000002`, etc.

You can also provide just the 6-digit code, and it will be automatically converted:

```python
from akshare_one.modules.historical.baostock import BaostockHistorical

# Automatic symbol conversion
provider = BaostockHistorical(
    symbol="600000",  # Will be converted to sh.600000
    interval="day"
)
```

### Supported Intervals

Baostock supports the following intervals:

- `day` - Daily data (most detailed)
- `week` - Weekly data
- `month` - Monthly data

Note: Baostock does not support minute or hour level data.

### Price Adjustment

Baostock supports three adjustment types:

- `none` (default) - Unadjusted prices
- `qfq` - Forward adjustment (前复权)
- `hfq` - Backward adjustment (后复权)

```python
# Get adjusted prices (forward adjustment)
provider = HistoricalDataFactory.get_provider(
    "baostock",
    symbol="sh.600000",
    interval="day",
    adjust="qfq"
)
df = provider.get_hist_data()
```

### Data Format

The returned DataFrame has the following columns:

- `timestamp` - Date/time with timezone
- `open` - Opening price
- `high` - Highest price
- `low` - Lowest price
- `close` - Closing price
- `volume` - Trading volume

## Examples

### Example 1: Fetch Daily Data

```python
from akshare_one.modules.historical import HistoricalDataFactory

provider = HistoricalDataFactory.get_provider(
    "baostock",
    symbol="sh.600000",  # 浦发银行
    interval="day",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

df = provider.get_hist_data()
print(f"数据行数: {len(df)}")
print(df.head())
```

### Example 2: Compare Multiple Stocks

```python
symbols = ["sh.600000", "sz.000001", "sh.601398"]

for symbol in symbols:
    provider = HistoricalDataFactory.get_provider(
        "baostock",
        symbol=symbol,
        interval="day",
        start_date="2024-01-01",
        end_date="2024-01-10"
    )
    df = provider.get_hist_data()
    print(f"{symbol}: {len(df)} rows")
```

### Example 3: Weekly Data

```python
provider = HistoricalDataFactory.get_provider(
    "baostock",
    symbol="sh.600000",
    interval="week",
    start_date="2024-01-01",
    end_date="2024-03-31"
)

df = provider.get_hist_data()
print(f"Weekly data: {len(df)} weeks")
```

## Limitations

1. **No Minute/Hour Data**: Baostock only provides daily, weekly, and monthly data.
2. **Login Required**: Baostock requires login before data retrieval (handled automatically).
3. **Symbol Format**: Must use `exchange.symbol` format (sh/sz prefix).
4. **Connection**: Uses socket connection to Baostock server (may need to logout manually in long-running applications).

## Comparison with Other Data Sources

| Feature | Baostock | EastMoney | Tushare |
|---------|----------|-----------|---------|
| Free Access | ✓ | ✓ | Partial (requires key) |
| API Key Required | ✗ | ✗ | ✓ |
| Minute Data | ✗ | ✓ | ✓ |
| Weekly/Monthly | ✓ | ✓ | ✓ |
| Price Adjustment | ✓ | ✓ | ✓ |
| Historical Range | Wide | Wide | Wide |

## Best Practices

1. **Use for Daily Data**: Baostock excels at providing reliable daily historical data.
2. **No API Key**: Ideal for projects that don't want to manage API keys.
3. **Logout Properly**: For long-running applications, consider calling `BaostockHistorical.logout()` when done.
4. **Symbol Conversion**: Use automatic symbol conversion for convenience.

## Error Handling

Common errors and solutions:

1. **Import Error**: Install baostock with `pip install baostock`
2. **Login Failed**: Check network connection to Baostock server
3. **Empty Data**: Check symbol format and date range
4. **Invalid Symbol**: Use correct exchange prefix (sh/sz)

## More Information

- Baostock Official Website: http://www.baostock.com/
- Baostock Documentation: http://www.baostock.com/mainContent?file=pythonAPI.md
- Baostock PyPI: https://pypi.org/project/baostock/