"""
Baostock Financial Data Usage Examples
=======================================

This module provides 6 financial data APIs from Baostock:

1. get_profit_data() - Profitability data (盈利能力)
2. get_operation_data() - Operation capability (营运能力)
3. get_growth_data() - Growth capability (成长能力)
4. get_balance_data() - Solvency data (偿债能力)
5. get_cash_flow_data() - Cash flow data (现金流量)
6. get_dupont_data() - DuPont analysis data (杜邦指数)

Basic Usage
-----------

Using the API endpoint functions:

```python
from akshare_one.modules.financial import get_profit_data

# Get profit data for stock 600000
df = get_profit_data(symbol="600000", year=2023, quarter=4)
print(df.head())

# Get operation data
df = get_operation_data(symbol="sh.600000", year=2023, quarter=4)
print(df.head())

# Get growth data
df = get_growth_data(symbol="600000", year=2023, quarter=4)
print(df.head())
```

Using the provider directly:

```python
from akshare_one.modules.financial import FinancialDataFactory

# Create provider
provider = FinancialDataFactory.get_provider("baostock", symbol="600000")

# Get all available profit data (no year/quarter specified)
df = provider.get_profit_data()
print(df.head())

# Get specific quarter data
df = provider.get_profit_data(year=2023, quarter=4)
print(df.head())

# With column filtering
df = provider.get_profit_data(
    year=2023, 
    quarter=4,
    columns=['roe', 'roa', 'net_profit']
)
print(df.head())

# With row filtering
df = provider.get_profit_data(
    year=2023,
    row_filter={'roe': {'min': 10}}  # Only rows with ROE >= 10%
)
print(df.head())
```

Symbol Formats
--------------

Baostock accepts symbols in two formats:

1. Full format with market prefix: "sh.600000", "sz.000001"
2. 6-digit code: "600000", "000001"

The provider automatically converts 6-digit codes to Baostock format:
- Codes starting with "6" or "9" -> Shanghai (sh.)
- Codes starting with "0", "3", "2" -> Shenzhen (sz.)

Examples:

```python
# These are all equivalent
provider = FinancialDataFactory.get_provider("baostock", symbol="600000")
provider = FinancialDataFactory.get_provider("baostock", symbol="sh.600000")

# For Shenzhen stocks
provider = FinancialDataFactory.get_provider("baostock", symbol="000001")
provider = FinancialDataFactory.get_provider("baostock", symbol="sz.000001")
```

Parameters
----------

year (optional): 
    - Query specific year (e.g., 2023)
    - If not specified, returns all available data

quarter (optional):
    - Query specific quarter (1, 2, 3, 4)
    - If not specified, returns all available data

columns (optional):
    - List of specific columns to return
    - Filters the output DataFrame

row_filter (optional):
    - Dictionary with filter conditions
    - Filters rows based on column values

Data Processing
---------------

All data returned is standardized:

- Column names are mapped to standard names
- Date fields are converted to datetime objects
- Numeric fields are properly typed
- Data is filtered based on provided criteria

The provider uses field mapping from configuration files to ensure
consistent column naming across different data sources.

Cache Behavior
--------------

All financial data methods use cache with 24-hour TTL:

- Cache is enabled by default
- Can be disabled with environment variable: AKSHARE_ONE_CACHE_ENABLED=false
- Cache key includes symbol, year, and quarter for proper differentiation

Login Management
----------------

Baostock requires login before querying data:

- Login is handled automatically by the provider
- Login state is shared across all instances (class-level)
- Logout can be called manually: BaostockFinancialProvider.logout()

```python
from akshare_one.modules.financial.baostock import BaostockFinancialProvider

# Logout when done (optional)
BaostockFinancialProvider.logout()

# Re-login happens automatically when needed
```

Error Handling
--------------

The provider handles errors gracefully:

- Login failures raise ConnectionError
- API failures raise ValueError with detailed message
- Empty results return empty DataFrame
- All operations are logged

Complete Example
----------------

```python
from akshare_one.modules.financial import (
    get_profit_data,
    get_operation_data,
    get_growth_data,
    get_balance_data,
    get_cash_flow_data,
    get_dupont_data,
)

# Analyze a company's financial health
symbol = "600000"
year = 2023
quarter = 4

# Get profitability metrics
profit_df = get_profit_data(symbol=symbol, year=year, quarter=quarter)
print("Profitability:", profit_df.columns.tolist())

# Get operation efficiency
operation_df = get_operation_data(symbol=symbol, year=year, quarter=quarter)
print("Operation:", operation_df.columns.tolist())

# Get growth metrics
growth_df = get_growth_data(symbol=symbol, year=year, quarter=quarter)
print("Growth:", growth_df.columns.tolist())

# Get solvency ratios
balance_df = get_balance_data(symbol=symbol, year=year, quarter=quarter)
print("Solvency:", balance_df.columns.tolist())

# Get cash flow indicators
cashflow_df = get_cash_flow_data(symbol=symbol, year=year, quarter=quarter)
print("Cash Flow:", cashflow_df.columns.tolist())

# Get DuPont analysis
dupont_df = get_dupont_data(symbol=symbol, year=year, quarter=quarter)
print("DuPont:", dupont_df.columns.tolist())
```

Integration with Multi-Source Framework
----------------------------------------

The Baostock provider integrates seamlessly with the multi-source framework:

```python
from akshare_one.modules.financial import FinancialDataFactory

# List all available sources
sources = FinancialDataFactory.list_sources()
print(f"Available sources: {sources}")  # ['baostock', 'tushare', ...]

# Use specific source
provider = FinancialDataFactory.get_provider("baostock", symbol="600000")

# Compare data from different sources
baostock_profit = FinancialDataFactory.get_provider("baostock", symbol="600000").get_profit_data()
tushare_profit = FinancialDataFactory.get_provider("tushare", symbol="600000").get_financial_metrics()

# Both use standardized field names for easy comparison
```

Testing
-------

Run the verification script to check implementation:

```bash
python verify_baostock_financial.py
```

Or test individual methods (requires Baostock service to be accessible):

```python
from akshare_one.modules.financial import get_profit_data

try:
    df = get_profit_data(symbol="600000", year=2023, quarter=4)
    print(f"Data fetched: {len(df)} rows")
except Exception as e:
    print(f"Error: {e}")
```
"""