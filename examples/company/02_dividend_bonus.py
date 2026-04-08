#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分红送转数据示例程序

本示例展示如何使用 akshare-one 的分红送转模块获取和分析数据。

依赖：
- pandas

运行方式：
    python examples/company/02_dividend_bonus.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#disclosure
"""

from datetime import datetime, timedelta

from akshare_one.modules.disclosure import (
    get_dividend_data,
    DisclosureFactory,
)
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_query_dividend_history():
    """场景 1：查询单个股票分红历史"""
    print("\n" + "=" * 80)
    print("场景 1：查询单个股票分红历史")
    print("=" * 80)

    try:
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365 * 5)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")

        df = get_dividend_data(symbol, start_date, end_date)

        if df.empty:
            print("无分红数据返回")
            return

        print("\n分红历史记录：")
        display_df = df[["fiscal_year", "dividend_per_share", "record_date", "ex_dividend_date", "payment_date"]]
        print(display_df.to_string(index=False))

        total_dividend = df["dividend_per_share"].sum()
        avg_dividend = df["dividend_per_share"].mean()
        max_dividend_row = df.loc[df["dividend_per_share"].idxmax()]

        print("\n统计分析：")
        print(f"累计分红总额：{total_dividend:.4f} 元/股")
        print(f"平均每年分红：{avg_dividend:.4f} 元/股")
        print(f"最高分红年份：{max_dividend_row['fiscal_year']}（{max_dividend_row['dividend_per_share']:.4f} 元/股）")
        print(f"分红次数：{len(df)} 次")

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


def scenario_2_query_recent_dividend_stocks():
    """场景 2：查询最近分红股票列表"""
    print("\n" + "=" * 80)
    print("场景 2：查询最近分红股票列表")
    print("=" * 80)

    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        print("\n查询范围：最近90天实施分红的股票")
        print(f"时间范围：{start_date} 至 {end_date}")

        symbol_list = ["600000", "601318", "600036", "000001", "000002"]

        all_dividend_data = []

        for symbol in symbol_list:
            try:
                df = get_dividend_data(symbol, start_date, end_date)
                if not df.empty:
                    all_dividend_data.append(df)
            except Exception:
                continue

        if not all_dividend_data:
            print("无分红数据返回")
            return

        combined_df = __import__("pandas").concat(all_dividend_data, ignore_index=True)

        print("\n最近分红股票列表：")
        display_df = combined_df[["symbol", "fiscal_year", "dividend_per_share", "ex_dividend_date"]].sort_values(
            "ex_dividend_date", ascending=False
        )
        print(display_df.to_string(index=False))

        print("\n统计分析：")
        print(f"分红股票数量：{combined_df['symbol'].nunique()} 只")
        print(f"分红总次数：{len(combined_df)} 次")

    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_3_calculate_dividend_yield():
    """场景 3：计算股息率"""
    print("\n" + "=" * 80)
    print("场景 3：计算股息率")
    print("=" * 80)

    try:
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")

        df = get_dividend_data(symbol, start_date, end_date)

        if df.empty:
            print("无分红数据返回，无法计算股息率")
            return

        latest_dividend = df.iloc[0]
        dividend_per_share = latest_dividend["dividend_per_share"]

        stock_price = 10.0

        dividend_yield = (dividend_per_share / stock_price) * 100

        print("\n分红信息：")
        print(f"年度：{latest_dividend['fiscal_year']}")
        print(f"每股分红：{dividend_per_share:.4f} 元")
        print(f"股权登记日：{latest_dividend['record_date']}")
        print(f"除权除息日：{latest_dividend['ex_dividend_date']}")

        print("\n股息率计算：")
        print(f"当前股价（示例）：{stock_price:.2f} 元")
        print(f"股息率：{dividend_yield:.2f}%")

        print("\n投资分析：")
        if dividend_yield >= 5:
            print("✓ 高股息股票，适合稳健型投资者")
        elif dividend_yield >= 3:
            print("✓ 中等股息，收益较为稳定")
        else:
            print("△ 股息率较低，主要依靠资本增值")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能在此期间没有分红记录")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_4_filter_high_dividend_stocks():
    """场景 4：高股息股票筛选"""
    print("\n" + "=" * 80)
    print("场景 4：高股息股票筛选")
    print("=" * 80)

    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print("\n筛选条件：股息率 >= 4% 的股票")
        print(f"时间范围：{start_date} 至 {end_date}")

        test_symbols = ["600000", "601318", "600036", "000001", "000002", "600019", "601288"]

        high_dividend_stocks = []

        for symbol in test_symbols:
            try:
                df = get_dividend_data(symbol, start_date, end_date)
                if not df.empty:
                    latest_dividend = df.iloc[0]
                    dividend_per_share = latest_dividend["dividend_per_share"]

                    stock_price = 10.0
                    dividend_yield = (dividend_per_share / stock_price) * 100

                    if dividend_yield >= 4.0:
                        high_dividend_stocks.append(
                            {
                                "symbol": symbol,
                                "fiscal_year": latest_dividend["fiscal_year"],
                                "dividend_per_share": dividend_per_share,
                                "estimated_price": stock_price,
                                "dividend_yield": dividend_yield,
                                "ex_dividend_date": latest_dividend["ex_dividend_date"],
                            }
                        )
            except Exception:
                continue

        if not high_dividend_stocks:
            print("未找到符合条件的高股息股票")
            return

        pd = __import__("pandas")
        result_df = pd.DataFrame(high_dividend_stocks)
        result_df = result_df.sort_values("dividend_yield", ascending=False)

        print("\n高股息股票列表：")
        display_df = result_df[["symbol", "fiscal_year", "dividend_per_share", "dividend_yield"]]
        print(display_df.to_string(index=False))

        print("\n筛选结果统计：")
        print(f"符合条件股票数量：{len(result_df)}")
        print(f"平均股息率：{result_df['dividend_yield'].mean():.2f}%")
        print(f"最高股息率：{result_df['dividend_yield'].max():.2f}%")
        print(f"最低股息率：{result_df['dividend_yield'].min():.2f}%")

    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_5_dividend_data_analysis():
    """场景 5：分红数据分析"""
    print("\n" + "=" * 80)
    print("场景 5：分红数据分析")
    print("=" * 80)

    try:
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365 * 10)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}（最近10年）")

        df = get_dividend_data(symbol, start_date, end_date)

        if df.empty:
            print("无分红数据返回")
            return

        print("\n分红历史数据：")
        print(df.to_string(index=False))

        df_sorted = df.sort_values("fiscal_year")

        print("\n分红趋势分析：")
        if len(df_sorted) >= 2:
            recent_5_years = df_sorted.tail(5)
            earlier_5_years = df_sorted.head(-5).tail(5) if len(df_sorted) > 5 else df_sorted.head(5)

            recent_avg = recent_5_years["dividend_per_share"].mean()
            earlier_avg = earlier_5_years["dividend_per_share"].mean()

            growth_rate = ((recent_avg - earlier_avg) / earlier_avg) * 100 if earlier_avg > 0 else 0

            print(f"最近5年平均分红：{recent_avg:.4f} 元/股")
            print(f"前期平均分红：{earlier_avg:.4f} 元/股")
            print(f"分红增长率：{growth_rate:.2f}%")

            if growth_rate > 10:
                print("趋势：分红增长强劲 ✓")
            elif growth_rate > 0:
                print("趋势：分红稳步增长")
            elif growth_rate > -10:
                print("趋势：分红略有下降")
            else:
                print("趋势：分红大幅下降，需关注 ⚠")

        print("\n分红稳定性分析：")
        dividend_std = df_sorted["dividend_per_share"].std()
        dividend_mean = df_sorted["dividend_per_share"].mean()
        cv = (dividend_std / dividend_mean) * 100 if dividend_mean > 0 else 0

        print(f"分红标准差：{dividend_std:.4f}")
        print(f"分红均值：{dividend_mean:.4f}")
        print(f"变异系数：{cv:.2f}%")

        if cv < 10:
            print("稳定性：分红非常稳定 ✓")
        elif cv < 20:
            print("稳定性：分红较为稳定")
        elif cv < 30:
            print("稳定性：分红波动适中")
        else:
            print("稳定性：分红波动较大 ⚠")

        print("\n分红连续性分析：")
        years = len(df_sorted)
        expected_years = 10

        continuity_rate = (years / expected_years) * 100

        print(f"10年内分红次数：{years} 次")
        print(f"分红连续性：{continuity_rate:.1f}%")

        if years == expected_years:
            print("评级：连续分红股票，分红记录优秀 ✓")
        elif years >= expected_years * 0.8:
            print("评级：分红较为连续")
        elif years >= expected_years * 0.5:
            print("评级：分红不太连续")
        else:
            print("评级：分红不连续 ⚠")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_6_multi_source_example():
    """场景 6：使用备用数据源（Sina）"""
    print("\n" + "=" * 80)
    print("场景 6：使用备用数据源（Sina）")
    print("=" * 80)

    try:
        available_sources = DisclosureFactory.get_available_sources()
        print(f"\n可用的数据源：{available_sources}")

        print("\n使用 Sina 数据源：")
        sina_provider = DisclosureFactory.get_provider("sina")
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}")
        print(f"时间范围：{start_date} 至 {end_date}")

        df = sina_provider.get_dividend_data(symbol, start_date, end_date)

        if df.empty:
            print("无分红数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("分红送转数据示例程序")
    print("=" * 80)

    scenario_1_query_dividend_history()
    scenario_2_query_recent_dividend_stocks()
    scenario_3_calculate_dividend_yield()
    scenario_4_filter_high_dividend_stocks()
    scenario_5_dividend_data_analysis()
    scenario_6_multi_source_example()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
