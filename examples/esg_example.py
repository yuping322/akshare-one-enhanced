#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESG 评级数据示例程序

本示例展示如何使用 akshare-one 的 ESG 评级模块获取和分析数据。

依赖：
- pandas

运行方式：
    python esg_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#esg
"""

from datetime import datetime, timedelta

# 导入模块
from akshare_one.modules.esg import (
    get_esg_rating,
    get_esg_rating_rank,
)
from akshare_one.modules.esg.factory import ESGFactory
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


def scenario_1_esg_rating_analysis():
    """场景 1：ESG 评级分析"""
    print("\n" + "=" * 80)
    print("场景 1：ESG 评级分析")
    print("=" * 80)

    try:
        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}（浦发银行）")
        print(f"时间范围：{start_date} 至 {end_date}")
        print("注意：ESG 数据获取较慢，请耐心等待...")

        df = get_esg_rating(symbol, start_date, end_date)

        # 数据处理
        if df.empty:
            print("该股票无 ESG 评级数据")
            return

        # 按评级日期排序
        df_sorted = df.sort_values("rating_date", ascending=False)

        # 结果展示：显示所有评级记录
        print("\nESG 评级历史记录：")
        display_df = df_sorted[
            ["rating_date", "esg_score", "e_score", "s_score", "g_score", "rating_agency"]
        ]
        print(display_df.to_string(index=False))

        # 统计分析
        latest = df_sorted.iloc[0]
        avg_esg = df["esg_score"].mean()

        print("\n统计分析：")
        print(f"最新评级日期：{latest['rating_date']}")
        print(f"最新 ESG 总分：{latest['esg_score']:.2f}")
        print(f"  环境得分（E）：{latest['e_score']:.2f}")
        print(f"  社会得分（S）：{latest['s_score']:.2f}")
        print(f"  治理得分（G）：{latest['g_score']:.2f}")
        print(f"评级机构：{latest['rating_agency']}")
        print(f"历史平均 ESG 得分：{avg_esg:.2f}")

        # 趋势分析
        if len(df) >= 2:
            oldest = df_sorted.iloc[-1]
            score_change = latest["esg_score"] - oldest["esg_score"]
            e_change = latest["e_score"] - oldest["e_score"]
            s_change = latest["s_score"] - oldest["s_score"]
            g_change = latest["g_score"] - oldest["g_score"]

            print(f"\n趋势分析（{oldest['rating_date']} 至 {latest['rating_date']}）：")
            print(f"ESG 总分变化：{score_change:+.2f}")
            print(f"  环境得分变化：{e_change:+.2f}")
            print(f"  社会得分变化：{s_change:+.2f}")
            print(f"  治理得分变化：{g_change:+.2f}")

            if score_change > 0:
                print("ESG 表现改善，评分上升")
            elif score_change < 0:
                print("ESG 表现下降，需要关注")
            else:
                print("ESG 表现稳定")

        # 评级等级判断
        if latest["esg_score"] >= 80:
            rating_level = "优秀"
        elif latest["esg_score"] >= 60:
            rating_level = "良好"
        elif latest["esg_score"] >= 40:
            rating_level = "中等"
        else:
            rating_level = "较差"

        print(f"\nESG 评级等级：{rating_level}（{latest['esg_score']:.2f} 分）")

        # 找出最弱项
        scores = {
            "环境（E）": latest["e_score"],
            "社会（S）": latest["s_score"],
            "治理（G）": latest["g_score"],
        }
        weakest = min(scores, key=lambda k: scores[k])
        print(f"需要改进的方面：{weakest}（{scores[weakest]:.2f} 分）")

    except InvalidParameterError as e:
        print(f"参数错误：{e}")
        print("提示：股票代码应为6位数字，如 '600000'")
    except NoDataError as e:
        print(f"无数据：{e}")
        print("提示：该股票可能没有 ESG 评级数据")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用：{e}")
        print("提示：数据源可能暂时无法访问，请稍后重试")
    except Exception as e:
        print(f"发生错误：{e}")
        print("提示：请检查网络连接或联系技术支持")


def scenario_2_industry_esg_comparison():
    """场景 2：行业 ESG 对比"""
    print("\n" + "=" * 80)
    print("场景 2：行业 ESG 对比")
    print("=" * 80)

    try:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        top_n = 20

        print(f"\n查询日期：{date}")
        print(f"排名数量：前 {top_n} 名")
        print("注意：ESG 数据获取较慢，请耐心等待...")

        df = get_esg_rating_rank(date, industry=None, top_n=top_n)

        # 数据处理
        if df.empty:
            print("无 ESG 评级排名数据")
            return

        # 结果展示：显示前20名
        print("\nESG 评级排名前20：")
        display_df = df.head(20)[
            ["rank", "symbol", "name", "esg_score", "industry", "industry_rank"]
        ]
        print(display_df.to_string(index=False))

        # 统计分析
        avg_score = df["esg_score"].mean()

        print("\n统计分析：")
        print(f"平均 ESG 得分：{avg_score:.2f}")
        print(
            f"最高得分：{df['esg_score'].max():.2f}（{df.loc[df['esg_score'].idxmax(), 'name']}）"
        )
        print(
            f"最低得分：{df['esg_score'].min():.2f}（{df.loc[df['esg_score'].idxmin(), 'name']}）"
        )

        # 按行业统计
        industry_stats = (
            df.groupby("industry")
            .agg({"esg_score": ["mean", "count"], "symbol": "count"})
            .reset_index()
        )
        industry_stats.columns = ["industry", "avg_score", "count1", "count2"]
        industry_stats = industry_stats[["industry", "avg_score", "count1"]]
        industry_stats.columns = ["industry", "avg_score", "count"]
        industry_stats = industry_stats.sort_values("avg_score", ascending=False)

        print("\n行业 ESG 平均得分排名：")
        for _, row in industry_stats.head(10).iterrows():
            print(f"  {row['industry']}: {row['avg_score']:.2f} 分（{row['count']} 家公司）")

        # 查询特定行业（银行业）的排名
        print("\n查询银行业 ESG 排名...")
        banking_df = get_esg_rating_rank(date, industry="银行", top_n=20)

        if not banking_df.empty:
            print("\n银行业 ESG 评级排名：")
            display_df = banking_df[["industry_rank", "symbol", "name", "esg_score", "rank"]]
            print(display_df.to_string(index=False))

            print("\n银行业统计：")
            print(f"平均 ESG 得分：{banking_df['esg_score'].mean():.2f}")
            print(
                f"行业内最高得分：{banking_df['esg_score'].max():.2f}（{banking_df.loc[banking_df['esg_score'].idxmax(), 'name']}）"
            )
        else:
            print("银行业暂无 ESG 评级数据")

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


def main():
    """运行所有场景"""
    print("=" * 80)
    print("ESG 评级数据示例程序")
    print("=" * 80)

    # 运行所有场景
    scenario_1_esg_rating_analysis()
    scenario_2_industry_esg_comparison()
    scenario_3_multi_source_example()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


def scenario_3_multi_source_example():
    """场景 3：使用备用数据源（Sina）"""
    print("\n" + "=" * 80)
    print("场景 3：使用备用数据源（Sina）")
    print("=" * 80)

    try:
        available_sources = ESGFactory.list_sources()
        print(f"\n可用的数据源：{available_sources}")

        print("\n使用 Sina 数据源：")
        sina_provider = ESGFactory.get_provider("sina")
        print(f"  提供商类型：{type(sina_provider).__name__}")
        print(f"  数据源名称：{sina_provider.get_source_name()}")

        symbol = "600000"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n查询股票：{symbol}")
        print("注意：跳过实际数据获取（ESG API 过慢）")

        # 注释掉实际的 API 调用以节省时间
        # df = sina_provider.get_esg_rating(symbol, start_date, end_date)
        # if df.empty:
        #     print("无 ESG 数据返回")
        # else:
        #     print(f"\n获取到 {len(df)} 条记录")
        #     print(df.head())
        print("(演示跳过实际 API 调用)")

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
