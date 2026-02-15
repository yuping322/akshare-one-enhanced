#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公告信披数据示例程序

本示例展示如何使用 akshare-one 的公告信披模块获取和分析数据。

依赖：
- pandas

运行方式：
    python disclosure_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#disclosure
"""

from datetime import datetime, timedelta

# 导入模块
from akshare_one.modules.disclosure import (
    get_disclosure_news,
    get_dividend_data,
    get_repurchase_data,
    get_st_delist_data,
)
from akshare_one.modules.disclosure.factory import DisclosureFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_monitor_dividend_announcements():
    """场景 1：监控分红公告"""
    print("\n" + "=" * 80)
    print("场景 1：监控分红公告")
    print("=" * 80)

    try:
        # 参数设置：查询浦发银行的分红历史
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365*3)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用
        df = get_dividend_data(symbol, start_date, end_date)

        # 数据处理
        if df.empty:
            print("无分红数据返回")
            return

        # 结果展示：显示所有分红记录
        print("\n分红历史记录：")
        display_df = df[['fiscal_year', 'dividend_per_share', 'record_date', 'ex_dividend_date', 'payment_date', 'dividend_ratio']]
        print(display_df.to_string(index=False))

        # 统计分析
        total_dividend = df['dividend_per_share'].sum()
        avg_dividend = df['dividend_per_share'].mean()
        max_dividend_year = df.loc[df['dividend_per_share'].idxmax()]

        print("\n统计分析：")
        print(f"累计分红总额：{total_dividend:.4f} 元/股")
        print(f"平均每年分红：{avg_dividend:.4f} 元/股")
        print(f"最高分红年份：{max_dividend_year['fiscal_year']}（{max_dividend_year['dividend_per_share']:.4f} 元/股）")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能在此期间没有分红记录")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_track_repurchase_progress():
    """场景 2：追踪股票回购进展"""
    print("\n" + "=" * 80)
    print("场景 2：追踪股票回购进展")
    print("=" * 80)

    try:
        # 参数设置：查询最近一年的回购公告
        symbol = None  # None 表示查询所有股票
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print("\n查询范围：所有股票")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用
        df = get_repurchase_data(symbol, start_date, end_date)

        # 数据处理
        if df.empty:
            print("无回购数据返回")
            return

        # 按回购金额排序
        df_sorted = df.sort_values('amount', ascending=False)

        # 结果展示：显示回购金额最大的前10条记录
        print("\n回购金额最大的前10条记录：")
        display_df = df_sorted.head(10)[['symbol', 'announcement_date', 'progress', 'amount', 'quantity', 'price_range']]
        print(display_df.to_string(index=False))

        # 统计分析
        total_amount = df['amount'].sum()
        total_quantity = df['quantity'].sum()
        repurchase_count = len(df)

        print("\n统计分析：")
        print(f"回购公告总数：{repurchase_count}")
        print(f"回购金额总计：{total_amount:,.2f} 万元")
        print(f"回购数量总计：{total_quantity:,.2f} 万股")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有回购公告")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_3_query_disclosure_news():
    """场景 3：查询公告信息"""
    print("\n" + "=" * 80)
    print("场景 3：查询公告信息")
    print("=" * 80)

    try:
        # 参数设置：查询浦发银行最近30天的所有公告
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        category = "all"

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")
        print(f"公告类别：{category}（所有类别）")

        # 接口调用
        df = get_disclosure_news(symbol, start_date, end_date, category)

        # 数据处理
        if df.empty:
            print("无公告数据返回")
            return

        # 结果展示：显示最近10条公告
        print("\n最近10条公告：")
        display_df = df.head(10)[['date', 'symbol', 'title', 'category']]
        print(display_df.to_string(index=False))

        # 按类别统计
        category_counts = df['category'].value_counts()

        print("\n按类别统计：")
        for cat, count in category_counts.items():
            print(f"{cat}: {count} 条")

        # 统计分析
        print("\n统计分析：")
        print(f"公告总数：{len(df)}")
        print(f"公告类别数：{len(category_counts)}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，类别应为 'all', 'dividend', 'repurchase', 'st', 'major_event' 之一")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有公告")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_4_query_st_delist_risk():
    """场景 4：ST 和退市风险查询"""
    print("\n" + "=" * 80)
    print("场景 4：ST 和退市风险查询")
    print("=" * 80)

    try:
        # 参数设置：查询所有 ST 和退市风险股票
        symbol = None  # None 表示查询所有股票

        print("\n查询范围：所有股票")

        # 接口调用
        df = get_st_delist_data(symbol)

        # 数据处理
        if df.empty:
            print("无 ST 或退市风险数据返回")
            return

        # 结果展示：显示前20条记录
        print("\nST 和退市风险股票（前20条）：")
        display_df = df.head(20)[['symbol', 'name', 'st_type', 'risk_level', 'announcement_date']]
        print(display_df.to_string(index=False))

        # 按风险等级统计
        risk_counts = df['risk_level'].value_counts()

        print("\n按风险等级统计：")
        for risk, count in risk_counts.items():
            print(f"{risk}: {count} 只")

        # 按 ST 类型统计
        st_type_counts = df['st_type'].value_counts()

        print("\n按 ST 类型统计：")
        for st_type, count in st_type_counts.items():
            print(f"{st_type}: {count} 只")

        # 统计分析
        print("\n统计分析：")
        print(f"风险股票总数：{len(df)}")
        print(f"风险等级种类：{len(risk_counts)}")
        print(f"ST 类型种类：{len(st_type_counts)}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：当前可能没有 ST 或退市风险股票")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("公告信披数据示例程序")
    print("=" * 80)

    # 运行所有场景
    scenario_1_monitor_dividend_announcements()
    scenario_2_track_repurchase_progress()
    scenario_3_query_disclosure_news()
    scenario_4_query_st_delist_risk()
    scenario_5_multi_source_example()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


def scenario_5_multi_source_example():
    """场景 5：使用备用数据源（Sina）"""
    print("\n" + "=" * 80)
    print("场景 5：使用备用数据源（Sina）")
    print("=" * 80)

    try:
        # 获取所有可用的数据源
        available_sources = DisclosureFactory.get_available_sources()
        print(f"\n可用的数据源：{available_sources}")

        # 使用备用数据源（Sina）
        print("\n使用 Sina 数据源：")
        sina_provider = DisclosureFactory.get_provider('sina')
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        # 使用 Sina 数据源获取数据
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 通过 provider 获取分红数据
        df = sina_provider.get_dividend_data(symbol, start_date, end_date)

        if df.empty:
            print("无分红数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
