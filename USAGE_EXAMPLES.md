# Efinance API Usage Examples

This document demonstrates the usage of the newly added efinance APIs for stock deal details and shareholder data.

## Deal Detail API (成交明细)

Get real-time stock deal details including time, price, volume, amount, and nature (buy/sell).

```python
from akshare_one import get_deal_detail

# Get deal details for a specific stock
df = get_deal_detail(
    stock_code='600000',  # 浦发银行
    max_count=100,         # Number of records to fetch
    source='efinance'
)

print(df.head())
# Columns: time, price, volume, amount, nature
# Example output:
#        time  price  volume  amount nature
# 0  14:59:59  10.50   1000   10500   买入
# 1  14:59:58  10.49    500    5245   卖出
```

## Top 10 Stock Holder Info API

Get information about the top 10 shareholders of a stock.

```python
from akshare_one import get_top10_stock_holder_info

# Get top 5 shareholders for 浦发银行
df = get_top10_stock_holder_info(
    stock_code='600000',
    top=5,
    source='efinance'
)

print(df.head())
# Columns: symbol, update_date, holder_code, holder_name, 
#          holding_shares, holding_ratio, change, change_rate
# Example output:
#   symbol update_date  holder_code  holder_name  holding_shares  ...
# 0  600000  2025-12-31    80008357  上海国际集团    4.25亿  ...
# 1  600000  2025-12-31    80043020  上海国有资产    7.19亿  ...
```

## Latest Holder Number API

Get the latest shareholder count for all stocks on a specific date.

```python
from akshare_one import get_latest_holder_number

# Get holder numbers for all stocks on a specific date
df = get_latest_holder_number(
    date='2025-03-31',  # Date in YYYY-MM-DD format
    source='efinance'
)

print(df.head())
# Columns: symbol, name, holder_number, date
# Example output:
#   symbol    name  holder_number        date
# 0  600777  *ST新潮          80403  2025-03-31
# 1  300225  *ST金泰          22682  2025-03-31
# 2  603380    易德龙          10578  2025-03-31

# Returns data for thousands of stocks
print(f"Total stocks: {len(df)}")  # Usually ~5000 stocks
```

## Using Provider Factory Pattern

You can also use the factory pattern to get provider instances:

```python
from akshare_one.modules.blockdeal import BlockDealFactory
from akshare_one.modules.shareholder import ShareholderFactory

# Get deal detail provider
blockdeal_provider = BlockDealFactory.get_provider('efinance')
df_deals = blockdeal_provider.get_deal_detail('600000', 50)

# Get shareholder provider
shareholder_provider = ShareholderFactory.get_provider('efinance')
df_holders = shareholder_provider.get_top10_stock_holder_info('600000', 10)
df_numbers = shareholder_provider.get_latest_holder_number('2025-03-31')
```

## Field Mapping

The APIs automatically map Chinese field names to standardized English names:

### Deal Detail Fields:
- 时间 → time
- 价格 → price  
- 成交量 → volume
- 成交额 → amount
- 性质 → nature (买入/卖出)
- 股票名称 → name
- 股票代码 → symbol
- 昨收 → prev_close
- 成交价 → deal_price
- 单数 → order_count

### Shareholder Fields:
- 股东名称 → holder_name
- 持股数量/持股数 → holding_shares
- 持股比例 → holding_ratio
- 更新日期 → update_date
- 股东代码 → holder_code
- 增减 → change
- 变动率 → change_rate
- 股东人数/股东户数 → holder_number

## Data Caching

The APIs use intelligent caching:
- Block deal and shareholder data cached for 24 hours (T+1 data)
- Cache can be disabled via environment variable: `AKSHARE_ONE_CACHE_ENABLED=false`

## Notes

1. **Deal Detail**: This API provides real-time transaction details during trading hours
2. **Top 10 Holders**: Updated quarterly/semi-annually, reflects the latest disclosed information
3. **Holder Number**: Returns shareholder count for all A-share stocks (~5000 stocks)
4. **Error Handling**: All APIs return empty DataFrame with appropriate columns on errors
5. **Data Source**: All APIs use `efinance` library as the underlying data source