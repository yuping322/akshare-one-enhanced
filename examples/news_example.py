#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻数据示例程序

本示例展示如何使用 akshare-one 的新闻模块获取个股和市场新闻数据。

依赖：
- pandas

运行方式：
    python news_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#news
"""

from akshare_one.modules.news import get_news_data
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_stock_news():
    """场景 1：获取个股新闻"""
    print("\n" + "=" * 80)
    print("场景 1：获取个股新闻")
    print("=" * 80)

    try:
        symbol = "300059"
        print(f"\n正在获取股票 {symbol} 的新闻数据...")

        df = get_news_data(symbol=symbol)

        if df.empty:
            print("无新闻数据返回")
            return

        print(f"\n获取到 {len(df)} 条新闻记录")
        print("\n新闻列表：")
        if "发布时间" in df.columns:
            print(df[["发布时间", "新闻标题"]].head(10).to_string(index=False))
        elif "title" in df.columns:
            print(df[["title", "time"]].head(10).to_string(index=False))
        else:
            print(df.head(10).to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_2_market_news():
    """场景 2：获取市场新闻"""
    print("\n" + "=" * 80)
    print("场景 2：获取市场新闻")
    print("=" * 80)

    try:
        print("\n正在获取市场新闻数据...")

        df = get_news_data()

        if df.empty:
            print("无新闻数据返回")
            return

        print(f"\n获取到 {len(df)} 条市场新闻")
        print("\n新闻列表：")
        print(df.head(10).to_string(index=False))

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("新闻数据示例程序")
    print("=" * 80)

    scenario_1_stock_news()
    scenario_2_market_news()

    print("\n" + "=" * 80)
    print("示例程序运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
