#!/usr/bin/env python3
"""
分析理杏仁API接入情况
"""

# 理杏仁所有API
LIXINGER_APIS = {
    "A股公司": [
        ("cn_company", "公司信息"),
        ("cn_company_allotment", "配股信息"),
        ("cn_company_announcement", "公告信息"),
        ("cn_company_block-deal", "大宗交易"),
        ("cn_company_candlestick", "K线数据"),
        ("cn_company_customers", "客户信息"),
        ("cn_company_dividend", "分红信息"),
        ("cn_company_equity-change", "股本变动"),
        ("cn_company_fs_non_financial", "财务数据"),
        ("cn_company_fund-collection-shareholders", "基金公司持股"),
        ("cn_company_fund-shareholders", "公募基金持股"),
        ("cn_company_fundamental_financial", "基本面数据(金融)"),
        ("cn_company_fundamental_non_financial", "基本面数据(非金融)"),
        ("cn_company_hot_tr_dri", "分红再投入收益率"),
        ("cn_company_indices", "股票所属指数"),
        ("cn_company_industries", "股票所属行业"),
        ("cn_company_inquiry", "问询函"),
        ("cn_company_major-shareholders-shares-change", "大股东增减持"),
        ("cn_company_majority-shareholders", "十大股东"),
        ("cn_company_margin-trading-and-securities-lending", "融资融券"),
        ("cn_company_measures", "监管措施"),
        ("cn_company_mutual-market", "互联互通"),
        ("cn_company_nolimit-shareholders", "十大流通股东"),
        ("cn_company_operating-data", "经营数据"),
        ("cn_company_operation-revenue-constitution", "营收构成"),
        ("cn_company_pledge", "股权质押"),
        ("cn_company_profile", "公司概况"),
        ("cn_company_senior-executive-shares-change", "高管增减持"),
        ("cn_company_shareholders-num", "股东人数"),
        ("cn_company_suppliers", "供应商"),
        ("cn_company_trading-abnormal", "龙虎榜"),
    ],
    "A股指数": [
        ("cn_index", "指数信息"),
        ("cn_index_candlestick", "指数K线"),
        ("cn_index_constituent-weightings", "成分权重"),
        ("cn_index_constituents", "成分股"),
        ("cn_index_drawdown", "回撤数据"),
        ("cn_index_fs_hybrid", "财务数据"),
        ("cn_index_fundamental", "基本面数据"),
        ("cn_index_hot_mm_ha", "互联互通"),
        ("cn_index_margin-trading-and-securities-lending", "融资融券"),
        ("cn_index_mutual-market", "互联互通"),
        ("cn_index_tracking-fund", "跟踪基金"),
    ],
    "A股行业": [
        ("cn_industry", "行业信息"),
        ("cn_industry_constituents_sw_2021", "行业成分股"),
        ("cn_industry_fs_sw_2021_hybrid", "行业财务数据"),
        ("cn_industry_fundamental_sw_2021", "行业基本面"),
        ("cn_industry_hot_mm_ha_sw_2021", "互联互通"),
        ("cn_industry_margin-trading-and-securities-lending_sw_2021", "融资融券"),
        ("cn_industry_mutual-market_sw_2021", "互联互通"),
    ],
    "A股基金": [
        ("cn_fund", "基金信息"),
        ("cn_fund-company", "基金公司信息"),
        ("cn_fund-company_asset-scale", "资产规模"),
        ("cn_fund-company_fund-list", "基金列表"),
        ("cn_fund-company_fund-manager-list", "基金经理列表"),
        ("cn_fund-company_hot_fc_as", "资产规模数据"),
        ("cn_fund-company_shareholdings", "持仓信息"),
        ("cn_fund-manager", "基金经理信息"),
        ("cn_fund-manager_hot_fmp", "基金经理收益率"),
        ("cn_fund-manager_management-funds", "管理基金"),
        ("cn_fund-manager_profit-ratio", "利润率"),
        ("cn_fund-manager_shareholdings", "持仓信息"),
        ("cn_fund_announcement", "公告信息"),
        ("cn_fund_asset-combination", "资产组合"),
        ("cn_fund_asset-industry-combination", "行业组合"),
        ("cn_fund_candlestick", "K线数据"),
        ("cn_fund_dividend", "分红信息"),
        ("cn_fund_drawdown", "回撤数据"),
        ("cn_fund_exchange-traded-close-price", "收盘价"),
        ("cn_fund_fees", "费用信息"),
        ("cn_fund_hot_f_nlacan", "溢价率"),
        ("cn_fund_manager", "基金经理"),
        ("cn_fund_net-value-of-dividend-reinvestment", "分红再投入净值"),
        ("cn_fund_net-value", "净值数据"),
        ("cn_fund_profile", "基金概况"),
        ("cn_fund_shareholders-structure", "持有人结构"),
        ("cn_fund_shareholdings", "持仓数据"),
        ("cn_fund_shares", "份额规模"),
        ("cn_fund_split", "拆分数据"),
        ("cn_fund_total-net-value", "累计净值"),
        ("cn_fund_turnover-rate", "换手率"),
    ],
    "港股": [
        ("hk_company", "港股公司信息"),
        ("hk_company_allotment", "配股信息"),
        ("hk_company_announcement", "公告信息"),
        ("hk_company_candlestick", "K线数据"),
        ("hk_company_dividend", "分红信息"),
        ("hk_company_employee", "员工数据"),
        ("hk_company_equity-change", "股本变动"),
        ("hk_company_fs_non_financial", "财务数据"),
        ("hk_company_fund-collection-shareholders", "基金持股"),
        ("hk_company_fund-shareholders", "基金持股"),
        ("hk_company_fundamental_non_financial", "基本面数据"),
        ("hk_company_hot_tr_dri", "分红再投入收益率"),
        ("hk_company_indices", "所属指数"),
        ("hk_company_industries", "所属行业"),
        ("hk_company_latest-shareholders", "最新股东"),
        ("hk_company_mutual-market", "互联互通"),
        ("hk_company_operation-revenue-constitution", "营收构成"),
        ("hk_company_profile", "公司概况"),
        ("hk_company_repurchase", "回购数据"),
        ("hk_company_shareholders-equity-change", "股东权益变动"),
        ("hk_company_short-selling", "做空数据"),
        ("hk_company_split", "拆分数据"),
        ("hk_index", "港股指数信息"),
        ("hk_index_candlestick", "指数K线"),
        ("hk_index_constituents", "成分股"),
        ("hk_index_drawdown", "回撤数据"),
        ("hk_index_fs_hybrid", "财务数据"),
        ("hk_index_fundamental", "基本面数据"),
        ("hk_index_hot_mm_ah", "互联互通"),
        ("hk_index_mutual-market", "互联互通"),
        ("hk_index_tracking-fund", "跟踪基金"),
        ("hk_industry", "港股行业信息"),
        ("hk_industry_constituents_hsi", "行业成分股"),
        ("hk_industry_fs_hsi_hybrid", "财务数据"),
        ("hk_industry_fundamental_hsi", "基本面数据"),
        ("hk_industry_hot_mm_ah_hsi", "互联互通"),
        ("hk_industry_mutual-market_hsi", "互联互通"),
    ],
    "美股": [
        ("us_index", "美股指数信息"),
        ("us_index_candlestick", "指数K线"),
        ("us_index_constituents", "成分股"),
        ("us_index_drawdown", "回撤数据"),
        ("us_index_fs_non_financial", "财务数据"),
        ("us_index_fundamental", "基本面数据"),
        ("us_index_hot_cp", "收盘点位"),
        ("us_index_hot_ifet_sni", "净流入数据"),
        ("us_index_tracking-fund", "跟踪基金"),
    ],
    "宏观": [
        ("macro_bop", "国际收支"),
        ("macro_central-bank-balance-sheet", "央行资产负债表"),
        ("macro_credit-securities-account", "信用证券账户"),
        ("macro_crude-oil", "原油数据"),
        ("macro_currency-exchange-rate", "汇率数据"),
        ("macro_domestic-debt-securities", "国内债券"),
        ("macro_domestic-trade", "社会消费品零售"),
        ("macro_energy", "能源数据"),
        ("macro_foreign-assets", "国外资产"),
        ("macro_foreign-trade", "对外贸易"),
        ("macro_gdp", "GDP数据"),
        ("macro_gold-price", "黄金数据"),
        ("macro_industrialization", "工业数据"),
        ("macro_interest-rates", "利率数据"),
        ("macro_investment-in-fixed-assets", "固定资产投资"),
        ("macro_investor", "投资者数据"),
        ("macro_leverage-ratio", "杠杆率"),
        ("macro_money-supply", "货币供应"),
        ("macro_national-debt", "国债数据"),
        ("macro_natural-gas", "天然气"),
        ("macro_non-ferrous-metals", "有色金属"),
        ("macro_official-reserve-assets", "官方储备资产"),
        ("macro_petroleum", "石油数据"),
        ("macro_platinum-price", "铂金数据"),
        ("macro_population", "人口数据"),
        ("macro_price-index", "价格指数(CPI)"),
        ("macro_real-estate", "房地产"),
        ("macro_required-reserves", "存款准备金率"),
        ("macro_rmb-deposits", "人民币存款"),
        ("macro_rmb-loans", "人民币贷款"),
        ("macro_rmbidx", "人民币指数"),
        ("macro_silver-price", "白银数据"),
        ("macro_social-financing", "社会融资"),
        ("macro_stamp-duty", "印花税"),
        ("macro_traffic-transportation", "交通运输"),
        ("macro_usdx", "美元指数"),
    ],
}

# 已接入的接口
IMPLEMENTED = {
    "valuation": ["cn_company_fundamental_non_financial"],
    "historical": ["cn_company_candlestick"],
    "index": ["cn_index", "cn_index_constituents", "cn_index_constituent-weightings", "cn_index_candlestick"],
    "margin": ["cn_company_margin-trading-and-securities-lending"],
    "macro": ["macro_price-index", "macro_money-supply", "macro_social-financing", "macro_interest-rates"],
}

# 对应的模块
MODULE_MAPPING = {
    "cn_company_block-deal": "blockdeal",
    "cn_company_dividend": "dividend",
    "cn_company_majority-shareholders": "shareholder",
    "cn_company_nolimit-shareholders": "shareholder",
    "cn_company_trading-abnormal": "lhb",
    "cn_company_pledge": "pledge",
    "cn_company_fs_non_financial": "financial",
    "cn_company_announcement": "disclosure",
    "cn_company_major-shareholders-shares-change": "insider",
    "cn_company_senior-executive-shares-change": "insider",
    "cn_company_fund-shareholders": "shareholder",
    "cn_fund": "etf",
    "cn_fund_shareholdings": "etf",
    "hk_company": "hkus",
    "hk_index": "hkus",
    "us_index": "hkus",
}


def analyze():
    """分析接入情况"""
    print("=" * 80)
    print("理杏仁 API 接入情况分析")
    print("=" * 80)

    # 统计总数
    total = sum(len(apis) for apis in LIXINGER_APIS.values())
    implemented_count = sum(len(apis) for apis in IMPLEMENTED.values())

    print(f"\n总API数量: {total}")
    print(f"已接入数量: {implemented_count}")
    print(f"接入率: {implemented_count / total * 100:.1f}%")

    # 已接入的API
    print("\n" + "=" * 80)
    print("已接入的API")
    print("=" * 80)
    for module, apis in IMPLEMENTED.items():
        print(f"\n{module}:")
        for api in apis:
            print(f"  ✓ {api}")

    # 重要的未接入API
    print("\n" + "=" * 80)
    print("重要未接入API (建议优先接入)")
    print("=" * 80)

    IMPORTANT_APIS = [
        ("cn_company_fs_non_financial", "财务数据", "financial"),
        ("cn_company_dividend", "分红数据", "disclosure"),
        ("cn_company_block-deal", "大宗交易", "blockdeal"),
        ("cn_company_majority-shareholders", "十大股东", "shareholder"),
        ("cn_company_nolimit-shareholders", "十大流通股东", "shareholder"),
        ("cn_company_trading-abnormal", "龙虎榜", "lhb"),
        ("cn_company_pledge", "股权质押", "pledge"),
        ("cn_company_announcement", "公司公告", "disclosure"),
        ("cn_company_major-shareholders-shares-change", "大股东增减持", "insider"),
        ("cn_company_senior-executive-shares-change", "高管增减持", "insider"),
        ("cn_company_fund-shareholders", "基金持股", "shareholder"),
        ("cn_fund_shareholdings", "基金持仓", "etf"),
        ("macro_gdp", "GDP数据", "macro"),
        ("macro_foreign-trade", "外贸数据", "macro"),
    ]

    for api, desc, module in IMPORTANT_APIS:
        implemented_apis = [item for sublist in IMPLEMENTED.values() for item in sublist]
        if api not in implemented_apis:
            print(f"  ⚠ {api:50s} {desc:15s} → {module}")

    # 可接入的API
    print("\n" + "=" * 80)
    print("可接入的API (有对应模块)")
    print("=" * 80)

    for category, apis in LIXINGER_APIS.items():
        print(f"\n【{category}】")
        for api, desc in apis:
            implemented_apis = [item for sublist in IMPLEMENTED.values() for item in sublist]
            if api not in implemented_apis:
                module = MODULE_MAPPING.get(api, "")
                if module:
                    print(f"  • {api:50s} {desc:15s} → {module}")
                else:
                    print(f"  ○ {api:50s} {desc:15s} (无对应模块)")


if __name__ == "__main__":
    analyze()
