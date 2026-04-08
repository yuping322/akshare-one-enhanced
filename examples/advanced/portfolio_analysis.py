#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级示例 2：组合分析

本示例展示如何使用 akshare-one 进行投资组合分析，包括：
- 获取多只股票数据
- 计算组合收益率
- 计算组合风险指标

运行方式：
    python examples/advanced/portfolio_analysis.py

注意：本示例仅供学习参考，不构成投资建议
"""

import pandas as pd
import numpy as np
from datetime import datetime
from akshare_one import get_hist_data, get_realtime_data


class PortfolioAnalysis:
    """投资组合分析"""

    def __init__(self, stocks, weights, start_date, end_date):
        """
        Args:
            stocks: 股票列表，如 ['600000', '000001', '600519']
            weights: 权重列表，如 [0.3, 0.3, 0.4]
            start_date: 开始日期
            end_date: 结束日期
        """
        self.stocks = stocks
        self.weights = weights
        self.start_date = start_date
        self.end_date = end_date
        self.stock_data = {}
        self.portfolio_df = None

    def load_data(self):
        """加载所有股票数据"""
        print("正在加载股票数据...")

        for symbol in self.stocks:
            print(f"  加载 {symbol}...")
            try:
                df = get_hist_data(
                    symbol=symbol,
                    interval="day",
                    start_date=self.start_date,
                    end_date=self.end_date,
                    adjust="qfq",
                    source="sina",
                )

                if not df.empty:
                    self.stock_data[symbol] = df
                    print(f"    成功: {len(df)} 条数据")
                else:
                    print(f"    无数据")
            except ConnectionError as e:
                print(f"    网络连接错误: {e}")
            except Exception as e:
                print(f"    加载失败: {e}")

        print(f"成功加载 {len(self.stock_data)} 只股票数据")

    def calculate_returns(self):
        """计算各股票收益率"""
        print("计算收益率...")

        for symbol, df in self.stock_data.items():
            df["pct_change"] = df["close"].pct_change()

    def calculate_portfolio_value(self):
        """计算组合净值"""
        print("计算组合净值...")

        # 初始净值设为1
        initial_value = 1.0

        # 创建组合DataFrame
        dates = None
        for symbol, df in self.stock_data.items():
            if dates is None:
                dates = df["timestamp"].values
            else:
                # 只保留所有股票都有的日期
                dates = np.intersect1d(dates, df["timestamp"].values)

        # 创建组合净值序列
        self.portfolio_df = pd.DataFrame({"timestamp": dates})

        # 计算组合收益率（加权平均）
        portfolio_returns = []

        for date in dates:
            daily_return = 0
            valid_stocks = 0

            for i, symbol in enumerate(self.stocks):
                if symbol in self.stock_data:
                    df = self.stock_data[symbol]
                    row = df[df["timestamp"] == date]

                    if not row.empty and pd.notna(row.iloc[0]["pct_change"]):
                        daily_return += row.iloc[0]["pct_change"] * self.weights[i]
                        valid_stocks += 1

            portfolio_returns.append(daily_return if valid_stocks > 0 else 0)

        self.portfolio_df["pct_change"] = portfolio_returns

        # 计算累计净值
        self.portfolio_df["net_value"] = (1 + self.portfolio_df["pct_change"]).cumprod()

    def calculate_risk_metrics(self):
        """计算风险指标"""
        if self.portfolio_df is None or self.portfolio_df.empty:
            return None

        df = self.portfolio_df

        # 年化收益率
        total_return = df["net_value"].iloc[-1] - 1
        days = len(df)
        annual_return = (1 + total_return) ** (252 / days) - 1 if days > 0 else 0

        # 波动率
        daily_std = df["pct_change"].std()
        annual_std = daily_std * np.sqrt(252)

        # 夏普比率（假设无风险利率为3%）
        risk_free_rate = 0.03
        sharpe_ratio = (annual_return - risk_free_rate) / annual_std if annual_std > 0 else 0

        # 最大回撤
        df["cummax"] = df["net_value"].cummax()
        df["drawdown"] = (df["net_value"] - df["cummax"]) / df["cummax"]
        max_drawdown = df["drawdown"].min()

        # Calmar比率
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

        return {
            "total_return": total_return,
            "annual_return": annual_return,
            "annual_std": annual_std,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "calmar_ratio": calmar_ratio,
        }

    def analyze_individual_stocks(self):
        """分析单只股票表现"""
        print("\n各股票表现：")
        print("-" * 60)

        for symbol, df in self.stock_data.items():
            if df.empty:
                continue

            # 计算收益率
            total_return = df["close"].iloc[-1] / df["close"].iloc[0] - 1

            # 计算波动率
            annual_std = df["pct_change"].std() * np.sqrt(252)

            print(f"\n股票 {symbol}:")
            print(f"  总收益率: {total_return:.2%}")
            print(f"  年化波动率: {annual_std:.2%}")

    def show_results(self):
        """显示分析结果"""
        print("\n" + "=" * 60)
        print("组合分析结果")
        print("=" * 60)

        # 显示组合构成
        print("\n组合构成：")
        for i, symbol in enumerate(self.stocks):
            print(f"  {symbol}: {self.weights[i]:.1%}")

        # 显示组合指标
        metrics = self.calculate_risk_metrics()

        if metrics:
            print("\n组合风险指标：")
            print(f"  总收益率: {metrics['total_return']:.2%}")
            print(f"  年化收益率: {metrics['annual_return']:.2%}")
            print(f"  年化波动率: {metrics['annual_std']:.2%}")
            print(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
            print(f"  最大回撤: {metrics['max_drawdown']:.2%}")
            print(f"  Calmar比率: {metrics['calmar_ratio']:.2f}")

        # 显示各股票表现
        self.analyze_individual_stocks()

        # 显示净值曲线
        if self.portfolio_df is not None and not self.portfolio_df.empty:
            print("\n组合净值曲线（月末）：")
            monthly = self.portfolio_df.groupby(self.portfolio_df["timestamp"].str[:7]).last()
            print(monthly[["net_value"]].head(12).to_string())


def example_equal_weight_portfolio():
    """示例1：等权重组合"""
    print("\n" + "=" * 60)
    print("示例1：等权重组合")
    print("=" * 60)

    stocks = ["600000", "000001", "600519", "000858"]
    weights = [0.25, 0.25, 0.25, 0.25]

    portfolio = PortfolioAnalysis(stocks=stocks, weights=weights, start_date="2024-01-01", end_date="2024-12-31")

    portfolio.load_data()
    portfolio.calculate_returns()
    portfolio.calculate_portfolio_value()
    portfolio.show_results()


def example_custom_weight_portfolio():
    """示例2：自定义权重组合"""
    print("\n" + "=" * 60)
    print("示例2：自定义权重组合")
    print("=" * 60)

    stocks = ["600000", "000001", "600519"]
    weights = [0.2, 0.3, 0.5]  # 重点配置贵州茅台

    portfolio = PortfolioAnalysis(stocks=stocks, weights=weights, start_date="2024-01-01", end_date="2024-12-31")

    portfolio.load_data()
    portfolio.calculate_returns()
    portfolio.calculate_portfolio_value()
    portfolio.show_results()


def example_comparison():
    """示例3：组合对比"""
    print("\n" + "=" * 60)
    print("示例3：不同组合对比")
    print("=" * 60)

    stocks = ["600000", "000001", "600519", "000858", "600036"]

    # 组合1：等权重
    portfolio1 = PortfolioAnalysis(stocks=stocks, weights=[0.2] * 5, start_date="2024-01-01", end_date="2024-12-31")

    portfolio1.load_data()
    portfolio1.calculate_returns()
    portfolio1.calculate_portfolio_value()
    metrics1 = portfolio1.calculate_risk_metrics()

    # 组合2：偏重白酒
    portfolio2 = PortfolioAnalysis(
        stocks=stocks,
        weights=[0.1, 0.1, 0.3, 0.3, 0.2],  # 贵州茅台和五粮液权重较高
        start_date="2024-01-01",
        end_date="2024-12-31",
    )

    portfolio2.stock_data = portfolio1.stock_data  # 复用数据
    portfolio2.calculate_returns()
    portfolio2.calculate_portfolio_value()
    metrics2 = portfolio2.calculate_risk_metrics()

    # 对比结果
    print("\n组合对比：")
    print("-" * 60)
    print(f"\n组合1（等权重）：")
    print(f"  年化收益率: {metrics1['annual_return']:.2%}")
    print(f"  夏普比率: {metrics1['sharpe_ratio']:.2f}")
    print(f"  最大回撤: {metrics1['max_drawdown']:.2%}")

    print(f"\n组合2（偏重白酒）：")
    print(f"  年化收益率: {metrics2['annual_return']:.2%}")
    print(f"  夏普比率: {metrics2['sharpe_ratio']:.2f}")
    print(f"  最大回撤: {metrics2['max_drawdown']:.2%}")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("投资组合分析示例")
    print("=" * 60)
    print("\n注意：本示例仅供学习，不构成投资建议")
    print("=" * 60)

    # 运行示例
    example_equal_weight_portfolio()
    example_custom_weight_portfolio()
    example_comparison()

    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
