#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期权数据示例程序

本示例展示如何使用 akshare-one 的期权模块获取和分析数据。

依赖：
- pandas

运行方式：
    python options_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#options
"""

from datetime import datetime, timedelta

from akshare_one.modules.options import OptionsDataFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_get_options_chain():
    """场景 1：获取期权链"""
    print("\n" + "=" * 80)
    print("场景 1：获取期权链")
    print("=" * 80)

    try:
        underlying_symbol = "AAPL"
        source = "sina"
        print(f"\n查询标的：{underlying_symbol}（苹果公司）")
        print(f"数据源：{source}")

        provider = OptionsDataFactory.get_provider(source, underlying_symbol=underlying_symbol)
        df = provider.get_options_chain()

        if df.empty:
            print("无期权链数据返回")
            return

        print(f"\n获取到期权链数据，共 {len(df)} 条记录")

        display_columns = [
            col
            for col in ["symbol", "name", "option_type", "strike", "expiration", "price", "pct_change", "volume"]
            if col in df.columns
        ]
        if display_columns:
            print("\n前10条期权数据：")
            print(df.head(10)[display_columns].to_string(index=False))
        else:
            print("\n前10条期权数据：")
            print(df.head(10).to_string(index=False))

        if "option_type" in df.columns:
            call_count = len(df[df["option_type"] == "call"]) if "option_type" in df.columns else 0
            put_count = len(df[df["option_type"] == "put"]) if "option_type" in df.columns else 0
            print(f"\n期权类型统计：")
            print(f"  看涨期权(CALL)：{call_count} 条")
            print(f"  看跌期权(PUT)：{put_count} 条")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：标的符号应为有效的股票代码")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该标的可能没有期权数据，请尝试其他标的")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_get_options_expirations():
    """场景 2：获取期权到期日"""
    print("\n" + "=" * 80)
    print("场景 2：获取期权到期日")
    print("=" * 80)

    try:
        underlying_symbol = "AAPL"
        source = "sina"
        print(f"\n查询标的：{underlying_symbol}（苹果公司）")
        print(f"数据源：{source}")

        provider = OptionsDataFactory.get_provider(source, underlying_symbol=underlying_symbol)
        result = provider.get_options_expirations(underlying_symbol=underlying_symbol)

        if isinstance(result, list):
            if not result:
                print("无到期日数据返回")
            else:
                print(f"\n获取到 {len(result)} 个到期日")
                print("\n可用到期日：")
                for exp in result[:10]:
                    print(f"  {exp}")
                if len(result) > 10:
                    print(f"  ... 还有 {len(result) - 10} 个")
        else:
            if result.empty:
                print("无到期日数据返回")
            else:
                print(f"\n获取到数据")
                print(result.to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_3_get_options_realtime():
    """场景 3：获取期权实时行情"""
    print("\n" + "=" * 80)
    print("场景 3：获取期权实时行情")
    print("=" * 80)

    try:
        underlying_symbol = "AAPL"
        symbol = "AAPL2505C200"
        source = "sina"
        print(f"\n查询标的：{underlying_symbol}")
        print(f"期权代码：{symbol}")
        print(f"数据源：{source}")

        provider = OptionsDataFactory.get_provider(source, underlying_symbol=underlying_symbol)
        df = provider.get_options_realtime(symbol=symbol)

        if df.empty:
            print("无实时行情数据返回")
            return

        print(f"\n获取到实时行情数据")

        display_columns = [
            col for col in ["symbol", "price", "change", "pct_change", "volume", "open_interest"] if col in df.columns
        ]
        if display_columns:
            print(df[display_columns].to_string(index=False))
        else:
            print(df.to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：期权代码格式不正确")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该期权代码可能不存在，请尝试其他代码")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_4_get_options_history():
    """场景 4：获取期权历史数据"""
    print("\n" + "=" * 80)
    print("场景 4：获取期权历史数据")
    print("=" * 80)

    try:
        underlying_symbol = "AAPL"
        symbol = "AAPL2505C200"
        source = "sina"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n查询期权代码：{symbol}")
        print(f"时间范围：{start_date} 至 {end_date}")
        print(f"数据源：{source}")

        provider = OptionsDataFactory.get_provider(source, underlying_symbol=underlying_symbol)
        df = provider.get_options_history(symbol=symbol, start_date=start_date, end_date=end_date)

        if df.empty:
            print("无历史数据返回")
            return

        print(f"\n获取到 {len(df)} 条历史数据")

        display_columns = [col for col in ["date", "open", "high", "low", "close", "volume"] if col in df.columns]
        if display_columns:
            print("\n最近10条历史数据：")
            print(df.head(10)[display_columns].to_string(index=False))
        else:
            print("\n最近10条历史数据：")
            print(df.head(10).to_string(index=False))

        if "close" in df.columns:
            valid_closes = df[df["close"].notna()]["close"]
            if len(valid_closes) > 0:
                latest = df.iloc[0]["close"] if len(df) > 0 else 0
                first = df.iloc[-1]["close"] if len(df) > 0 else 0
                change = latest - first if (latest and first) else 0
                change_pct = (change / first * 100) if first != 0 else 0

                print(f"\n历史价格统计：")
                print(f"  最新收盘价：{latest:.2f}")
                print(f"  期初收盘价：{first:.2f}")
                print(f"  价格变化：{change:+.2f}（{change_pct:+.2f}%）")
                print(f"  最高价：{valid_closes.max():.2f}")
                print(f"  最低价：{valid_closes.min():.2f}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：日期格式应为 YYYY-MM-DD")
    except NoDataError as e:
        print(f"无数据：{e}")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_5_multi_source_example():
    """场景 5：使用备用数据源"""
    print("\n" + "=" * 80)
    print("场景 5：使用备用数据源")
    print("=" * 80)

    try:
        available_sources = OptionsDataFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        if not available_sources:
            print("没有可用的数据源")
            return

        source = available_sources[0] if available_sources else None
        if source:
            print(f"\n使用 {source} 数据源：")
            underlying_symbol = "AAPL"
            provider = OptionsDataFactory.get_provider(source, underlying_symbol=underlying_symbol)
            print(f"  提供商类型：{type(provider).__name__}")
            print(f"  数据源名称：{provider.get_source_name()}")
            print(f"  标的符号：{provider.underlying_symbol}")

            print(f"\n尝试获取 {underlying_symbol} 的期权链...")

            df = provider.get_options_chain()

            if df.empty:
                print("无期权链数据返回")
            else:
                print(f"获取到 {len(df)} 条记录")
                print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("期权数据示例程序")
    print("=" * 80)

    scenario_1_get_options_chain()
    scenario_2_get_options_expirations()
    scenario_3_get_options_realtime()
    scenario_4_get_options_history()
    scenario_5_multi_source_example()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
