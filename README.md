<div align="center">
  <h1>AKShare One</h1>
  <div>
    <a href="README_zh.md">中文</a> | <strong>English</strong>
  </div>
</div>

**AKShare One** is a data interface for obtaining Chinese A-shares, based on [AKShare](https://github.com/akfamily/akshare). It aims to simplify AKShare's usage and unify input/output formats from different data sources, making it easier to pass data to LLM.

## ✨ Features

- 📊 Unified stock code formats across data sources
- 🏗️ Standardized return data structures
- 🛠️ Simplified API parameter design
- ⏱️ Automatic timestamp and adjustment handling

## 🚀 Core Features

### Basic Data Interfaces

| Function | Interface |
|------|------|
| Historical data | `get_hist_data` |
| Real-time quotes | `get_realtime_data` |
| Stock news | `get_news_data` |
| Financial data | `get_balance_sheet`/`get_income_statement`/`get_cash_flow` |
| Futures data | `get_futures_hist_data`/`get_futures_realtime_data` |
| Options data | `get_options_chain`/`get_options_realtime`/`get_options_hist` |
| Internal transactions | `get_inner_trade_data` |
| Basic stock info | `get_basic_info` |
| Financial metrics | `get_financial_metrics` |
| Technical indicators | See [indicators.py](src/akshare_one/indicators.py) |

### Market Data Extension Interfaces (New)

| Module | Main Interfaces | Description |
|---------|---------|------|
| **Fund Flow** | `get_stock_fund_flow`<br>`get_sector_fund_flow`<br>`get_main_fund_flow_rank` | Stock/sector fund flow, main fund ranking |
| **Disclosure** | `get_disclosure_news`<br>`get_dividend_data`<br>`get_repurchase_data`<br>`get_st_delist_data` | Announcements, dividends, buybacks, ST/delisting risks |
| **Northbound** | `get_northbound_flow`<br>`get_northbound_holdings`<br>`get_northbound_top_stocks` | Northbound capital flow, holdings, rankings |
| **Macro Data** | `get_lpr_rate`<br>`get_pmi_index`<br>`get_cpi_data`<br>`get_m2_supply`<br>`get_shibor_rate` | LPR rates, PMI index, CPI/PPI, M2 supply, Shibor rates |
| **Block Deal** | `get_block_deal`<br>`get_block_deal_summary` | Block trade details and statistics |
| **Dragon Tiger** | `get_dragon_tiger_list`<br>`get_dragon_tiger_summary`<br>`get_dragon_tiger_broker_stats` | Dragon-tiger list data, statistics, broker analysis |
| **Limit Up/Down** | `get_limit_up_pool`<br>`get_limit_down_pool`<br>`get_limit_up_stats` | Limit up/down pools and statistics |
| **Margin Trading** | `get_margin_data`<br>`get_margin_summary` | Margin trading data and market summary |
| **Equity Pledge** | `get_equity_pledge`<br>`get_equity_pledge_ratio_rank` | Equity pledge data and ratio rankings |
| **Restricted Release** | `get_restricted_release`<br>`get_restricted_release_calendar` | Restricted share release data and calendar |
| **Goodwill** | `get_goodwill_data`<br>`get_goodwill_impairment`<br>`get_goodwill_by_industry` | Goodwill data, impairment expectations, industry stats |
| **ESG Rating** | `get_esg_rating`<br>`get_esg_rating_rank` | ESG scores and rankings |

## 📦 Quick Installation

```bash
pip install akshare-one
```

## 💻 Usage Example

### Basic Data Retrieval

```python
from akshare_one import get_hist_data
from akshare_one.indicators import get_sma

# Get historical data
df = get_hist_data(
    symbol="600000",
    interval="day",
    adjust="hfq"
)

# Calculate 20-day Simple Moving Average
df_sma = get_sma(df, window=20)
```

### Fund Flow Analysis

```python
from akshare_one.modules.fundflow import (
    get_stock_fund_flow,
    get_sector_fund_flow,
    get_main_fund_flow_rank
)

# Get stock fund flow
fund_flow = get_stock_fund_flow(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Get sector fund flow
sector_flow = get_sector_fund_flow(
    sector_type="industry",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Get main fund flow ranking
rank = get_main_fund_flow_rank(
    date="2024-12-31",
    indicator="net_inflow"
)
```

### Disclosure Monitoring

```python
from akshare_one.modules.disclosure import (
    get_disclosure_news,
    get_dividend_data,
    get_repurchase_data
)

# Get disclosure news
news = get_disclosure_news(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-12-31",
    category="all"
)

# Get dividend data
dividend = get_dividend_data(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

### Northbound Capital Tracking

```python
from akshare_one.modules.northbound import (
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks
)

# Get northbound capital flow
flow = get_northbound_flow(
    start_date="2024-01-01",
    end_date="2024-12-31",
    market="all"
)

# Get northbound holdings
holdings = get_northbound_holdings(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

### Macro Data Analysis

```python
from akshare_one.modules.macro import (
    get_lpr_rate,
    get_pmi_index,
    get_cpi_data
)

# Get LPR rates
lpr = get_lpr_rate(
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Get PMI index
pmi = get_pmi_index(
    start_date="2024-01-01",
    end_date="2024-12-31",
    pmi_type="manufacturing"
)
```

## 📚 Documentation

Full API documentation is now available on GitHub Pages:

https://zwldarren.github.io/akshare-one/
