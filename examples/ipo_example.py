#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPO数据示例程序

本示例展示如何使用 akshare-one 的IPO模块获取和分析新股数据。

依赖：
- pandas

运行方式：
    python ipo_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#ipo
"""

from akshare_one import get_new_stocks, get_ipo_info
from akshare_one.modules.ipo import IPOFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_get_new_stocks():
    """场景 1：获取新股列表"""
    print("\n" + "=" * 80)
    print("场景 1：获取新股列表")
    print("=" * 80)

    try:
        df = get_new_stocks()

        if df.empty:
            print("无新股数据返回")
            print("提示：可能当前没有新股申购或数据尚未更新")
            return

        print(f"\n获取到 {len(df)} 只新股")
        print("\n新股列表：")
        print(df.to_string(index=False))

        if "issue_price" in df.columns:
            total_amount = (
                df["issue_price"].sum() if "shares" not in df.columns else (df["issue_price"] * df["shares"]).sum()
            )
            print(f"\n预计募集资金：{total_amount:,.2f} 万元")

        if "listing_date" in df.columns:
            upcoming = df[df["listing_date"].notna()]
            if not upcoming.empty:
                print(f"\n即将上市：{len(upcoming)} 只")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：当前可能没有新股数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_get_ipo_info():
    """场景 2：获取IPO详细信息"""
    print("\n" + "=" * 80)
    print("场景 2：获取IPO详细信息")
    print("=" * 80)

    try:
        df = get_ipo_info()

        if df.empty:
            print("无IPO信息返回")
            print("提示：可能当前没有IPO数据或数据尚未更新")
            return

        print(f"\n获取到 {len(df)} 条IPO信息")
        print("\nIPO信息：")
        print(df.to_string(index=False))

        if "issue_size" in df.columns:
            total_size = df["issue_size"].sum()
            print(f"\n总发行规模：{total_size:,.2f} 万股")

        if "pe_ratio" in df.columns:
            avg_pe = df["pe_ratio"].mean()
            print(f"平均市盈率：{avg_pe:.2f}")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
    except NoDataError as e:
        print(f"无数据：{e}")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def scenario_3_statistics():
    """场景 3：IPO统计分析"""
    print("\n" + "=" * 80)
    print("场景 3：IPO统计分析")
    print("=" * 80)

    try:
        df_stocks = get_new_stocks()
        df_ipo = get_ipo_info()

        print(f"\n新股数量：{len(df_stocks)}")
        print(f"IPO信息数量：{len(df_ipo)}")

        if not df_ipo.empty:
            if "industry" in df_ipo.columns:
                print("\n按行业统计IPO：")
                industry_counts = df_ipo["industry"].value_counts()
                for ind, count in industry_counts.head(5).items():
                    print(f"  {ind}: {count} 只")

            if "issue_price" in df_ipo.columns:
                print(f"\n发行价统计：")
                print(f"  最高价：{df_ipo['issue_price'].max():.2f} 元")
                print(f"  最低价：{df_ipo['issue_price'].min():.2f} 元")
                print(f"  平均价：{df_ipo['issue_price'].mean():.2f} 元")

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_4_multi_source():
    """场景 4：使用多数据源获取IPO数据"""
    print("\n" + "=" * 80)
    print("场景 4：使用多数据源获取IPO数据")
    print("=" * 80)

    try:
        available_sources = IPOFactory.get_available_sources()
        print(f"\n可用的数据源：{available_sources}")

        for source in available_sources:
            try:
                df = get_new_stocks(source=source)
                if not df.empty:
                    print(f"\n{source} 数据源返回新股：")
                    print(f"  记录数: {len(df)}")
                else:
                    print(f"\n{source} 数据源: 无新股数据返回")
            except Exception as e:
                print(f"\n{source} 数据源失败: {e}")

        for source in available_sources:
            try:
                df = get_ipo_info(source=source)
                if not df.empty:
                    print(f"\n{source} 数据源返回IPO信息：")
                    print(f"  记录数: {len(df)}")
                else:
                    print(f"\n{source} 数据源: 无IPO信息返回")
            except Exception as e:
                print(f"\n{source} 数据源失败: {e}")

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("IPO数据示例程序")
    print("=" * 80)

    scenario_1_get_new_stocks()
    scenario_2_get_ipo_info()
    scenario_3_statistics()
    scenario_4_multi_source()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
