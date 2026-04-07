# AkShare Version Compatibility Report

Generated: 2026-04-04T09:02:00.042130

## Version Summary

| Version | Total Functions | Available | Unavailable | Success Rate |
|---------|----------------|-----------|-------------|-------------|
| 1.18.23 | 43 | 40 | 3 | 55.8% |

## Version 1.18.23

Test Time: 2026-04-04T09:01:17.158184

### Function Details

| Function | Exists | Test Passed | Return Type | Error |
|----------|--------|-------------|-------------|-------|
| stock_zh_a_hist | ✓ | ✗ | None | Call failed: HTTPSConnectionPool(host='push2his.ea... |
| stock_zh_a_hist_min_em | ✓ | ✗ | None | Call failed: HTTPSConnectionPool(host='push2his.ea... |
| stock_zh_a_spot_em | ✓ | ✗ | None | Call failed: HTTPSConnectionPool(host='82.push2.ea... |
| stock_individual_info_em | ✓ | ✗ | None | Call failed: HTTPSConnectionPool(host='push2.eastm... |
| fund_etf_hist_sina | ✓ | ✓ | DataFrame |  |
| stock_dzjy_mrtj | ✓ | ✓ | DataFrame |  |
| stock_dzjy_mrmx | ✓ | ✓ | DataFrame |  |
| stock_individual_fund_flow | ✓ | ✓ | DataFrame |  |
| stock_individual_fund_flow_rank | ✓ | ✗ | None | Call failed: HTTPSConnectionPool(host='push2.eastm... |
| stock_sector_fund_flow_rank | ✓ | ✗ | None | Call failed: HTTPSConnectionPool(host='push2.eastm... |
| stock_board_industry_name_em | ✓ | ✗ | None | Call failed: HTTPSConnectionPool(host='17.push2.ea... |
| stock_board_industry_cons_em | ✓ | ✗ | None | Call failed: stock_board_industry_cons_em() got an... |
| stock_board_concept_name_em | ✓ | ✗ | None | Call failed: HTTPSConnectionPool(host='79.push2.ea... |
| stock_board_concept_cons_em | ✓ | ✗ | None | Call failed: stock_board_concept_cons_em() got an ... |
| macro_china_gdp | ✓ | ✓ | DataFrame |  |
| macro_china_cpi | ✓ | ✓ | DataFrame |  |
| macro_china_ppi | ✓ | ✓ | DataFrame |  |
| stock_hsgt_north_net_flow_in_em | ✗ | ✗ | None | Function 'stock_hsgt_north_net_flow_in_em' not fou... |
| stock_hsgt_north_acc_flow_in_em | ✗ | ✗ | None | Function 'stock_hsgt_north_acc_flow_in_em' not fou... |
| stock_hsgt_hist_em | ✓ | ✓ | DataFrame |  |
| stock_hsgt_individual_em | ✓ | ✗ | None | Call failed: 'NoneType' object is not subscriptabl... |
| stock_hsgt_hold_stock_em | ✓ | ✓ | DataFrame |  |
| stock_financial_report_sina | ✓ | ✓ | DataFrame |  |
| stock_margin_detail_szse | ✓ | ✓ | DataFrame |  |
| stock_margin_detail_sse | ✓ | ✓ | DataFrame |  |
| stock_gpzy_pledge_ratio_em | ✓ | ✓ | DataFrame |  |
| stock_gpzy_pledge_ratio_detail_em | ✓ | ✗ | None | Call failed: stock_gpzy_pledge_ratio_detail_em() g... |
| stock_lhb_detail_em | ✓ | ✗ | None | Call failed: 'NoneType' object is not subscriptabl... |
| stock_lhb_stock_statistic_em | ✓ | ✓ | DataFrame |  |
| stock_zt_pool_em | ✓ | ✓ | DataFrame |  |
| stock_zt_pool_previous_em | ✓ | ✓ | DataFrame |  |
| stock_notice_report | ✓ | ✓ | DataFrame |  |
| stock_esg_rate_sina | ✓ | ✗ | None | Call failed: stock_esg_rate_sina() got an unexpect... |
| stock_em_yjbb | ✗ | ✗ | None | Function 'stock_em_yjbb' not found |
| futures_zh_minute_sina | ✓ | ✓ | DataFrame |  |
| futures_zh_daily_sina | ✓ | ✓ | DataFrame |  |
| futures_zh_realtime | ✓ | ✓ | DataFrame |  |
| option_current_em | ✓ | ✗ | None | Call failed: HTTPSConnectionPool(host='23.push2.ea... |
| option_sse_daily_sina | ✓ | ✓ | DataFrame |  |
| index_stock_info | ✓ | ✓ | DataFrame |  |
| index_zh_a_hist | ✓ | ✗ | None | Call failed: HTTPSConnectionPool(host='80.push2.ea... |
| bond_cb_jsl | ✓ | ✓ | DataFrame |  |
| tool_trade_date_hist_sina | ✓ | ✓ | DataFrame |  |

## Unavailable Functions

The following functions are not available in one or more versions:

- stock_em_yjbb
- stock_hsgt_north_acc_flow_in_em
- stock_hsgt_north_net_flow_in_em

## Recommendations

**Recommended Version:** 1.18.23

This version has the highest success rate (55.8%).
