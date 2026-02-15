#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商誉数据示例程序

本示例展示如何使用 akshare-one 的商誉模块获取和分析数据。

依赖：
- pandas

运行方式：
    python goodwill_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#goodwill
"""

from datetime import datetime, timedelta

# 导入模块
from akshare_one.modules.goodwill import (
    get_goodwill_data,
    get_goodwill_impairment,
    get_goodwill_by_industry,
)
from akshare_one.modules.goodwill.factory import GoodwillFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_monitor_impairment_risk():
    """场景 1：监控商誉减值风险"""
    print("\n" + "=" * 80)
    print("场景 1：监控商誉减值风险")
    print("=" * 80)

    try:
        # 参数设置：查询最近一个交易日的商誉减值预期
        # 避免使用今天的日期，因为数据通常T+1更新
        date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        print(f"\n查询日期：{date}")

        # 接口调用 - 增加错误处理
        try:
            df = get_goodwill_impairment(date)
        except Exception as e:
            print(f"接口调用失败: {e}")
            print("尝试使用更早的日期...")
            # 尝试使用更早的日期，因为商誉数据更新频率较低
            date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            print(f"重试使用日期: {date}")
            df = get_goodwill_impairment(date)

        # 数据处理
        if df.empty:
            print("无商誉减值预期数据")
            return

        # 按风险等级排序
        risk_order = {'high': 0, 'medium': 1, 'low': 2}
        df['risk_order'] = df['risk_level'].map(risk_order)
        df_sorted = df.sort_values(['risk_order', 'expected_impairment'], ascending=[True, False])

        # 结果展示：显示前20条记录
        print("\n商誉减值风险排名（前20）：")
        display_df = df_sorted.head(20)[['symbol', 'name', 'goodwill_balance', 'expected_impairment', 'risk_level']]
        print(display_df.to_string(index=False))

        # 统计分析
        total_goodwill = df['goodwill_balance'].sum()
        total_impairment = df['expected_impairment'].sum()

        print("\n统计分析：")
        print(f"涉及公司总数：{len(df)}")
        print(f"商誉总额：{total_goodwill:,.2f} 元")
        print(f"预期减值总额：{total_impairment:,.2f} 元")
        print(f"预期减值比例：{(total_impairment/total_goodwill*100):.2f}%")

        # 按风险等级统计
        risk_stats = df.groupby('risk_level').agg({
            'symbol': 'count',
            'goodwill_balance': 'sum',
            'expected_impairment': 'sum'
        }).reset_index()
        risk_stats.columns = ['risk_level', 'count', 'goodwill_balance', 'expected_impairment']

        print("\n按风险等级统计：")
        for _, row in risk_stats.iterrows():
            print(f"  {row['risk_level']}: {row['count']} 家公司，商誉 {row['goodwill_balance']:,.2f} 元，预期减值 {row['expected_impairment']:,.2f} 元")

        # 高风险公司提示
        high_risk = df[df['risk_level'] == 'high']
        if not high_risk.empty:
            print(f"\n高风险公司（共 {len(high_risk)} 家）：")
            for _, row in high_risk.head(10).iterrows():
                impairment_ratio = (row['expected_impairment'] / row['goodwill_balance'] * 100) if row['goodwill_balance'] > 0 else 0
                print(f"  {row['symbol']} {row['name']}: 商誉 {row['goodwill_balance']:,.2f} 元，预期减值 {row['expected_impairment']:,.2f} 元（{impairment_ratio:.1f}%）")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该日期可能没有数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_industry_comparison():
    """场景 2：行业商誉对比"""
    print("\n" + "=" * 80)
    print("场景 2：行业商誉对比")
    print("=" * 80)

    try:
        # 参数设置：查询最近一个季度的行业商誉统计
        # 商誉数据通常按季度更新
        date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        print(f"\n查询日期：{date}")

        # 接口调用 - 增加错误处理
        try:
            df = get_goodwill_by_industry(date)
        except Exception as e:
            print(f"接口调用失败: {e}")
            print("尝试使用更早的日期...")
            # 尝试使用更早的日期
            date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
            print(f"重试使用日期: {date}")
            df = get_goodwill_by_industry(date)

        # 数据处理
        if df.empty:
            print("无行业商誉统计数据")
            return

        # 按商誉总额排序
        df_sorted = df.sort_values('total_goodwill', ascending=False)

        # 结果展示：显示前15个行业
        print("\n行业商誉排名（前15）：")
        display_df = df_sorted.head(15)[['industry', 'total_goodwill', 'avg_ratio', 'total_impairment', 'company_count']]
        print(display_df.to_string(index=False))

        # 统计分析
        total_goodwill = df['total_goodwill'].sum()
        total_impairment = df['total_impairment'].sum()
        total_companies = df['company_count'].sum()

        print("\n统计分析：")
        print(f"行业总数：{len(df)}")
        print(f"涉及公司总数：{total_companies}")
        print(f"商誉总额：{total_goodwill:,.2f} 元")
        print(f"减值总额：{total_impairment:,.2f} 元")
        print(f"整体减值比例：{(total_impairment/total_goodwill*100):.2f}%")

        # 找出高风险行业（平均商誉占净资产比例高）
        high_ratio_industries = df[df['avg_ratio'] > 30].sort_values('avg_ratio', ascending=False)
        if not high_ratio_industries.empty:
            print("\n高商誉占比行业（平均商誉/净资产 > 30%）：")
            for _, row in high_ratio_industries.head(10).iterrows():
                print(f"  {row['industry']}: 平均占比 {row['avg_ratio']:.2f}%，{row['company_count']} 家公司，商誉总额 {row['total_goodwill']:,.2f} 元")

        # 找出减值严重的行业
        df['impairment_ratio'] = (df['total_impairment'] / df['total_goodwill'] * 100).fillna(0)
        high_impairment = df[df['impairment_ratio'] > 10].sort_values('impairment_ratio', ascending=False)
        if not high_impairment.empty:
            print("\n减值严重行业（减值比例 > 10%）：")
            for _, row in high_impairment.head(10).iterrows():
                print(f"  {row['industry']}: 减值比例 {row['impairment_ratio']:.2f}%，减值总额 {row['total_impairment']:,.2f} 元")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该日期可能没有数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_3_query_stock_goodwill():
    """场景 3：查询个股商誉数据"""
    print("\n" + "=" * 80)
    print("场景 3：查询个股商誉数据")
    print("=" * 80)

    try:
        # 参数设置：查询浦发银行的商誉数据
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365*3)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用
        df = get_goodwill_data(symbol, start_date, end_date)

        # 数据处理
        if df.empty:
            print("该股票无商誉数据")
            return

        # 按报告日期排序
        df_sorted = df.sort_values('report_date', ascending=False)

        # 结果展示：显示所有记录
        print("\n商誉数据历史记录：")
        display_df = df_sorted[['report_date', 'goodwill_balance', 'goodwill_ratio', 'goodwill_impairment']]
        print(display_df.to_string(index=False))

        # 统计分析
        latest = df_sorted.iloc[0]
        total_impairment = df['goodwill_impairment'].sum()

        print("\n统计分析：")
        print(f"最新报告期：{latest['report_date']}")
        print(f"最新商誉余额：{latest['goodwill_balance']:,.2f} 元")
        print(f"商誉占净资产比例：{latest['goodwill_ratio']:.2f}%")
        print(f"累计商誉减值：{total_impairment:,.2f} 元")

        # 趋势分析
        if len(df) >= 2:
            oldest = df_sorted.iloc[-1]
            balance_change = latest['goodwill_balance'] - oldest['goodwill_balance']
            ratio_change = latest['goodwill_ratio'] - oldest['goodwill_ratio']

            print(f"\n趋势分析（{oldest['report_date']} 至 {latest['report_date']}）：")
            print(f"商誉余额变化：{balance_change:,.2f} 元（{(balance_change/oldest['goodwill_balance']*100):.2f}%）")
            print(f"商誉占比变化：{ratio_change:.2f} 个百分点")

            if balance_change < 0:
                print("商誉余额下降，可能存在减值或资产处置")
            elif balance_change > 0:
                print("商誉余额上升，可能有新的并购活动")

        # 风险评估
        if latest['goodwill_ratio'] > 50:
            print(f"\n风险提示：商誉占净资产比例较高（{latest['goodwill_ratio']:.2f}%），存在较大减值风险")
        elif latest['goodwill_ratio'] > 30:
            print(f"\n风险提示：商誉占净资产比例适中（{latest['goodwill_ratio']:.2f}%），需要持续关注")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能没有商誉数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("商誉数据示例程序")
    print("=" * 80)

    # 运行所有场景
    scenario_1_monitor_impairment_risk()
    scenario_2_industry_comparison()
    scenario_3_query_stock_goodwill()
    scenario_4_multi_source_example()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


def scenario_4_multi_source_example():
    """场景 4：使用备用数据源（Sina）"""
    print("\n" + "=" * 80)
    print("场景 4：使用备用数据源（Sina）")
    print("=" * 80)

    try:
        # 获取所有可用的数据源
        available_sources = GoodwillFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        # 使用备用数据源（Sina）
        print("\n使用 Sina 数据源：")
        sina_provider = GoodwillFactory.get_provider('sina')
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        # 使用 Sina 数据源获取数据
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}")

        # 通过 provider 获取数据
        df = sina_provider.get_goodwill_data(symbol, start_date, end_date)

        if df.empty:
            print("无商誉数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
