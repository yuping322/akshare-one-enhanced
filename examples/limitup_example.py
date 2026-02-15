#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停池数据示例程序

本示例展示如何使用 akshare-one 的涨停池模块获取和分析数据。

依赖：
- pandas

运行方式：
    python limitup_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#limitup
"""

from datetime import datetime, timedelta

# 导入模块
from akshare_one.modules.limitup import (
    get_limit_up_pool,
    get_limit_down_pool,
    get_limit_up_stats,
)
from akshare_one.modules.limitup.factory import LimitUpDownFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_limit_up_pool():
    """场景 1：监控涨停池"""
    print("\n" + "=" * 80)
    print("场景 1：监控涨停池")
    print("=" * 80)

    try:
        # 获取最近一个交易日的日期（假设为昨天）
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        print(f"\n正在获取 {date} 的涨停股票...")

        # 调用接口获取涨停池数据
        df = get_limit_up_pool(date)

        # 数据处理
        if df.empty:
            print("当日无涨停股票")
            return

        # 结果展示
        print(f"\n{date} 涨停股票池（共 {len(df)} 只）：")
        print(df[['symbol', 'name', 'close_price', 'limit_up_time',
                  'open_count', 'consecutive_days', 'turnover_rate']].head(20).to_string(index=False))

        # 统计分析
        print("\n统计信息：")
        print(f"涨停股票总数：{len(df)} 只")
        print(f"一字板数量（未打开）：{(df['open_count'] == 0).sum()} 只")
        print(f"打开过的涨停板：{(df['open_count'] > 0).sum()} 只")
        print(f"连板股票（连续2天及以上）：{(df['consecutive_days'] >= 2).sum()} 只")

        # 找出最强势的股票（一字板且连板）
        strong_stocks = df[(df['open_count'] == 0) & (df['consecutive_days'] >= 2)]
        if not strong_stocks.empty:
            print("\n最强势股票（一字板连板）：")
            print(strong_stocks[['symbol', 'name', 'consecutive_days', 'reason']].head(10).to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该日期可能不是交易日或数据尚未更新")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_limit_down_pool():
    """场景 2：监控跌停池"""
    print("\n" + "=" * 80)
    print("场景 2：监控跌停池")
    print("=" * 80)

    try:
        # 获取最近一个交易日的日期（假设为昨天）
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        print(f"\n正在获取 {date} 的跌停股票...")

        # 调用接口获取跌停池数据
        df = get_limit_down_pool(date)

        # 数据处理
        if df.empty:
            print("当日无跌停股票")
            return

        # 结果展示
        print(f"\n{date} 跌停股票池（共 {len(df)} 只）：")
        print(df[['symbol', 'name', 'close_price', 'limit_down_time',
                  'open_count', 'turnover_rate']].head(20).to_string(index=False))

        # 统计分析
        print("\n统计信息：")
        print(f"跌停股票总数：{len(df)} 只")
        print(f"一字跌停（未打开）：{(df['open_count'] == 0).sum()} 只")
        print(f"打开过的跌停板：{(df['open_count'] > 0).sum()} 只")
        print(f"平均换手率：{df['turnover_rate'].mean():.2f}%")

        # 找出最弱势的股票（一字跌停）
        weak_stocks = df[df['open_count'] == 0]
        if not weak_stocks.empty:
            print("\n最弱势股票（一字跌停）：")
            print(weak_stocks[['symbol', 'name', 'close_price', 'limit_down_time']].head(10).to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该日期可能不是交易日或数据尚未更新")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_3_market_sentiment():
    """场景 3：分析市场情绪"""
    print("\n" + "=" * 80)
    print("场景 3：分析市场情绪")
    print("=" * 80)

    try:
        # 获取最近 10 个交易日的统计数据
        end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")

        print(f"\n正在获取 {start_date} 至 {end_date} 的涨跌停统计...")

        # 调用接口获取涨停统计数据
        df = get_limit_up_stats(start_date, end_date)

        # 数据处理
        if df.empty:
            print("无统计数据")
            return

        # 过滤掉周末和无数据的日期
        df = df[(df['limit_up_count'] > 0) | (df['limit_down_count'] > 0)]

        if df.empty:
            print("该时间段内无涨跌停数据")
            return

        # 结果展示
        print("\n涨跌停统计数据：")
        print(df.to_string(index=False))

        # 市场情绪分析
        print("\n市场情绪分析：")
        avg_limit_up = df['limit_up_count'].mean()
        avg_limit_down = df['limit_down_count'].mean()
        avg_broken_rate = df['broken_rate'].mean()

        print(f"平均每日涨停数量：{avg_limit_up:.1f} 只")
        print(f"平均每日跌停数量：{avg_limit_down:.1f} 只")
        print(f"平均炸板率：{avg_broken_rate:.2f}%")

        # 计算涨跌停比率
        total_limit_up = df['limit_up_count'].sum()
        total_limit_down = df['limit_down_count'].sum()

        if total_limit_down > 0:
            ratio = total_limit_up / total_limit_down
            print(f"涨跌停比率：{ratio:.2f}")

            # 判断市场情绪
            if ratio > 2:
                sentiment = "强势（涨停远多于跌停）"
            elif ratio > 1:
                sentiment = "偏强（涨停多于跌停）"
            elif ratio > 0.5:
                sentiment = "偏弱（跌停多于涨停）"
            else:
                sentiment = "弱势（跌停远多于涨停）"

            print(f"市场情绪：{sentiment}")
        else:
            print("市场情绪：强势（无跌停股票）")

        # 炸板率分析
        if avg_broken_rate > 50:
            print(f"炸板率分析：炸板率较高（{avg_broken_rate:.2f}%），市场承接力较弱")
        elif avg_broken_rate > 30:
            print(f"炸板率分析：炸板率适中（{avg_broken_rate:.2f}%），市场情绪一般")
        else:
            print(f"炸板率分析：炸板率较低（{avg_broken_rate:.2f}%），市场承接力强")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("涨停池数据示例程序")
    print("=" * 80)

    # 运行所有场景
    scenario_1_limit_up_pool()
    scenario_2_limit_down_pool()
    scenario_3_market_sentiment()
    scenario_4_multi_source_example()

    print("\n" + "=" * 80)
    print("示例程序运行完成")
    print("=" * 80)


def scenario_4_multi_source_example():
    """场景 4：使用备用数据源（Sina）"""
    print("\n" + "=" * 80)
    print("场景 4：使用备用数据源（Sina）")
    print("=" * 80)

    try:
        # 获取所有可用的数据源
        available_sources = LimitUpDownFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        # 使用备用数据源（Sina）
        print("\n使用 Sina 数据源：")
        sina_provider = LimitUpDownFactory.get_provider('sina')
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        # 使用 Sina 数据源获取数据
        date = datetime.now().strftime("%Y-%m-%d")

        print(f"\n查询日期：{date}")

        # 通过 provider 获取数据
        df = sina_provider.get_limit_up_pool(date)

        if df.empty:
            print("无涨停池数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
