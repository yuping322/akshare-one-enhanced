#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大宗交易数据示例程序

本示例展示如何使用 akshare-one 的大宗交易模块获取和分析数据。

依赖：
- pandas

运行方式：
    python blockdeal_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#blockdeal
"""

from datetime import datetime, timedelta

# 导入模块
from akshare_one.modules.blockdeal import (
    get_block_deal,
    get_block_deal_summary,
)
from akshare_one.modules.blockdeal.factory import BlockDealFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_identify_block_deals():
    """场景 1：识别大宗交易"""
    print("\n" + "=" * 80)
    print("场景 1：识别大宗交易")
    print("=" * 80)

    try:
        # 参数设置：查询浦发银行最近60天的大宗交易
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 接口调用 - 修复参数不匹配问题
        # 根据源码分析，get_block_deal 接口参数正确，但可能需要调整日期格式
        try:
            df = get_block_deal(symbol, start_date, end_date)
        except Exception as e:
            print(f"接口调用失败: {e}")
            print("尝试使用不同的参数格式...")
            # 尝试使用更宽泛的日期范围
            wider_start = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            df = get_block_deal(symbol, wider_start, end_date)

        # 数据处理
        if df.empty:
            print("无大宗交易数据返回")
            return

        # 结果展示：显示所有大宗交易记录
        print(f"\n大宗交易明细（共 {len(df)} 笔）：")
        display_df = df[['date', 'symbol', 'name', 'price', 'volume', 'amount', 'premium_rate']]
        print(display_df.to_string(index=False))

        # 计算溢价率统计
        avg_premium = df['premium_rate'].mean()
        max_premium = df['premium_rate'].max()
        min_premium = df['premium_rate'].min()
        premium_deals = len(df[df['premium_rate'] > 0])
        discount_deals = len(df[df['premium_rate'] < 0])

        print("\n溢价率分析：")
        print(f"平均溢价率：{avg_premium:.2f}%")
        print(f"最高溢价率：{max_premium:.2f}%")
        print(f"最低溢价率：{min_premium:.2f}%")
        print(f"溢价交易笔数：{premium_deals}")
        print(f"折价交易笔数：{discount_deals}")

        # 统计分析
        total_amount = df['amount'].sum()
        total_volume = df['volume'].sum()
        avg_price = df['price'].mean()

        print("\n交易统计：")
        print(f"交易总额：{total_amount:,.2f} 元")
        print(f"交易总量：{total_volume:,.0f} 股")
        print(f"平均成交价：{avg_price:.2f} 元")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有大宗交易数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_analyze_block_deal_summary():
    """场景 2：分析大宗交易统计"""
    print("\n" + "=" * 80)
    print("场景 2：分析大宗交易统计")
    print("=" * 80)

    try:
        # 参数设置：查询最近30天的大宗交易统计
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n时间范围：{start_date} 至 {end_date}")

        # 场景 2.1：按股票分组统计
        print("\n--- 按股票分组统计 ---")
        try:
            df_stock = get_block_deal_summary(start_date, end_date, group_by="stock")
        except Exception as e:
            print(f"获取股票分组统计失败: {e}")
            # 尝试使用更近的日期范围
            recent_start = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
            df_stock = get_block_deal_summary(recent_start, end_date, group_by="stock")

        if df_stock.empty:
            print("无按股票分组的统计数据")
        else:
            # 按交易笔数排序，显示前10名
            df_stock_sorted = df_stock.sort_values('deal_count', ascending=False).head(10)
            print("\n大宗交易最活跃的股票（前10名）：")
            display_cols = ['symbol', 'name', 'deal_count', 'total_amount', 'avg_premium_rate']
            print(df_stock_sorted[display_cols].to_string(index=False))

            # 统计分析
            total_stocks = len(df_stock)
            total_deals = df_stock['deal_count'].sum()
            total_amount = df_stock['total_amount'].sum()
            avg_premium = df_stock['avg_premium_rate'].mean()

            print("\n股票统计：")
            print(f"涉及股票数量：{total_stocks} 只")
            print(f"交易总笔数：{total_deals} 笔")
            print(f"交易总金额：{total_amount:,.2f} 元")
            print(f"平均溢价率：{avg_premium:.2f}%")

        # 场景 2.2：按日期分组统计
        print("\n--- 按日期分组统计 ---")
        try:
            df_date = get_block_deal_summary(start_date, end_date, group_by="date")
        except Exception as e:
            print(f"获取日期分组统计失败: {e}")
            recent_start = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
            df_date = get_block_deal_summary(recent_start, end_date, group_by="date")

        if df_date.empty:
            print("无按日期分组的统计数据")
        else:
            # 显示最近10个交易日
            df_date_sorted = df_date.sort_values('date', ascending=False).head(10)
            print("\n最近10个交易日的大宗交易统计：")
            display_cols = ['date', 'deal_count', 'total_amount', 'avg_premium_rate']
            print(df_date_sorted[display_cols].to_string(index=False))

            # 找出交易最活跃的日期
            most_active_date = df_date.loc[df_date['deal_count'].idxmax()]
            print(f"\n交易最活跃日期：{most_active_date['date']}")
            print(f"  交易笔数：{most_active_date['deal_count']} 笔")
            print(f"  交易金额：{most_active_date['total_amount']:,.2f} 元")

        # 场景 2.3：按营业部分组统计
        print("\n--- 按营业部分组统计 ---")
        try:
            df_broker = get_block_deal_summary(start_date, end_date, group_by="broker")
        except Exception as e:
            print(f"获取营业部分组统计失败: {e}")
            recent_start = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
            df_broker = get_block_deal_summary(recent_start, end_date, group_by="broker")

        if df_broker.empty:
            print("无按营业部分组的统计数据")
        else:
            # 按交易笔数排序，显示前10名
            df_broker_sorted = df_broker.sort_values('deal_count', ascending=False).head(10)
            print("\n最活跃的营业部（前10名）：")
            display_cols = ['broker_name', 'deal_count', 'total_amount', 'avg_premium_rate']
            print(df_broker_sorted[display_cols].to_string(index=False))

            # 统计分析
            total_brokers = len(df_broker)
            print("\n营业部统计：")
            print(f"参与营业部数量：{total_brokers} 家")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：请检查日期格式是否正确（YYYY-MM-DD）")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该时间段可能没有大宗交易数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_3_multi_source_example():
    """场景 3：使用备用数据源（Sina）"""
    print("\n" + "=" * 80)
    print("场景 3：使用备用数据源（Sina）")
    print("=" * 80)

    try:
        # 获取所有可用的数据源
        available_sources = BlockDealFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        # 使用备用数据源（Sina）
        print("\n使用 Sina 数据源：")
        sina_provider = BlockDealFactory.get_provider('sina')
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        # 使用 Sina 数据源获取数据
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}")
        print(f"时间范围：{start_date} 至 {end_date}")

        # 通过 provider 获取数据
        df = sina_provider.get_block_deal(symbol, start_date, end_date)

        if df.empty:
            print("无大宗交易数据返回")
        else:
            print(f"\n获取到 {len(df)} 条记录")
            print(df.head())

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("大宗交易数据示例程序")
    print("=" * 80)

    # 运行所有场景
    scenario_1_identify_block_deals()
    scenario_2_analyze_block_deal_summary()
    scenario_3_multi_source_example()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
