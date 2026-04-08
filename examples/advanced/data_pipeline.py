#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级示例 4：数据管道

本示例展示如何构建简单的数据管道，包括：
- 批量获取数据
- 数据清洗和处理
- 数据存储

运行方式：
    python examples/advanced/data_pipeline.py

注意：本示例仅供学习参考
"""

import os
import time
from datetime import datetime, timedelta
import pandas as pd
from akshare_one import get_hist_data, get_realtime_data, get_basic_info


class DataPipeline:
    """数据管道"""

    def __init__(self, output_dir=None):
        self.output_dir = output_dir or os.path.join("/tmp", "akshare_one", "examples", "data_pipeline")
        os.makedirs(self.output_dir, exist_ok=True)

        self.stocks = []
        self.data_cache = {}

    def add_stock(self, symbol):
        """添加股票到监控列表"""
        if symbol not in self.stocks:
            self.stocks.append(symbol)
            print(f"已添加股票: {symbol}")

    def add_stocks(self, symbols):
        """批量添加股票"""
        for symbol in symbols:
            self.add_stock(symbol)

    def fetch_daily_data(self, start_date, end_date):
        """获取日线数据"""
        print("\n正在获取日线数据...")

        for symbol in self.stocks:
            try:
                print(f"  获取 {symbol}...")
                df = get_hist_data(
                    symbol=symbol,
                    interval="day",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq",
                    source="sina",
                )

                if not df.empty:
                    self.data_cache[f"{symbol}_daily"] = df
                    print(f"    成功: {len(df)} 条")

                time.sleep(0.1)  # 避免请求过快

            except Exception as e:
                print(f"    失败: {e}")

        print(f"完成，成功获取 {len(self.data_cache)} 只股票数据")

    def fetch_realtime_data(self):
        """获取实时数据"""
        print("\n正在获取实时数据...")
        print("注意：实时数据源当前不可用，跳过")
        self.data_cache["realtime"] = {}
        print("完成，跳过实时数据获取")

    def process_data(self):
        """数据处理"""
        print("\n正在处理数据...")

        processed = {}

        for key, data in self.data_cache.items():
            if key == "realtime" or key == "processed":
                continue

            if not isinstance(data, pd.DataFrame):
                continue

            symbol = key.replace("_daily", "")

            # 计算技术指标
            df = data.copy()

            if df.empty or "close" not in df.columns:
                print(f"    跳过 {symbol}: 无有效数据")
                continue

            # 涨跌幅
            df["pct_change"] = df["close"].pct_change() * 100

            # 均线
            df["ma5"] = df["close"].rolling(window=5).mean()
            df["ma10"] = df["close"].rolling(window=10).mean()
            df["ma20"] = df["close"].rolling(window=20).mean()

            # 成交量均线
            df["volume_ma5"] = df["volume"].rolling(window=5).mean()

            # 价格波动
            df["price_range"] = df["high"] - df["low"]

            processed[key] = df

        self.data_cache["processed"] = processed
        print(f"完成，处理了 {len(processed)} 只股票数据")

    def calculate_statistics(self):
        """计算统计指标"""
        print("\n正在计算统计指标...")

        stats_summary = []

        for key, df in self.data_cache.get("processed", {}).items():
            symbol = key.replace("_daily", "")

            if df.empty or "close" not in df.columns:
                continue

            # 统计信息
            stats = {
                "symbol": symbol,
                "data_count": len(df),
                "start_date": df["timestamp"].iloc[0] if len(df) > 0 else "",
                "end_date": df["timestamp"].iloc[-1] if len(df) > 0 else "",
                "avg_close": df["close"].mean(),
                "max_close": df["close"].max(),
                "min_close": df["close"].min(),
                "avg_volume": df["volume"].mean(),
                "avg_pct_change": df["pct_change"].mean(),
                "max_pct_change": df["pct_change"].max(),
                "min_pct_change": df["pct_change"].min(),
            }

            stats_summary.append(stats)

        self.data_cache["statistics"] = pd.DataFrame(stats_summary)
        print(f"完成，统计了 {len(stats_summary)} 只股票")

    def save_data(self):
        """保存数据"""
        print("\n正在保存数据...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存日线数据
        daily_dir = os.path.join(self.output_dir, "daily")
        os.makedirs(daily_dir, exist_ok=True)

        for key, df in self.data_cache.items():
            if key in ["realtime", "processed", "statistics"]:
                continue

            symbol = key.replace("_daily", "")
            filename = os.path.join(daily_dir, f"{symbol}_{timestamp}.csv")
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"  保存: {filename}")

        # 保存处理后的数据
        processed_dir = os.path.join(self.output_dir, "processed")
        os.makedirs(processed_dir, exist_ok=True)

        for key, df in self.data_cache.get("processed", {}).items():
            symbol = key.replace("_daily", "")
            filename = os.path.join(processed_dir, f"{symbol}_processed_{timestamp}.csv")
            df.to_csv(filename, index=False, encoding="utf-8-sig")

        print(f"  保存处理后的数据到: {processed_dir}")

        # 保存实时数据
        realtime_dir = os.path.join(self.output_dir, "realtime")
        os.makedirs(realtime_dir, exist_ok=True)

        realtime_combined = []
        for symbol, df in self.data_cache.get("realtime", {}).items():
            realtime_combined.append(df)

        if realtime_combined:
            realtime_df = pd.concat(realtime_combined, ignore_index=True)
            filename = os.path.join(realtime_dir, f"realtime_{timestamp}.csv")
            realtime_df.to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"  保存实时数据到: {filename}")

        # 保存统计数据
        stats_dir = os.path.join(self.output_dir, "statistics")
        os.makedirs(stats_dir, exist_ok=True)

        if "statistics" in self.data_cache:
            filename = os.path.join(stats_dir, f"statistics_{timestamp}.csv")
            self.data_cache["statistics"].to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"  保存统计数据到: {filename}")

        print("保存完成")

    def show_summary(self):
        """显示摘要"""
        print("\n" + "=" * 60)
        print("数据管道摘要")
        print("=" * 60)

        print(f"\n监控股票数: {len(self.stocks)}")
        print(f"缓存数据类型: {len(self.data_cache)}")

        if "statistics" in self.data_cache:
            print("\n统计数据概览：")
            print(self.data_cache["statistics"].to_string(index=False))

    def run_full_pipeline(self, start_date, end_date):
        """运行完整的数据管道"""
        print("\n" + "=" * 60)
        print("运行数据管道")
        print("=" * 60)

        # 1. 获取日线数据
        self.fetch_daily_data(start_date, end_date)

        # 2. 获取实时数据
        self.fetch_realtime_data()

        # 3. 处理数据
        self.process_data()

        # 4. 计算统计指标
        self.calculate_statistics()

        # 5. 保存数据
        self.save_data()

        # 6. 显示摘要
        self.show_summary()

        print("\n" + "=" * 60)
        print("数据管道运行完成")
        print("=" * 60)


def example_daily_pipeline():
    """示例1：日线数据管道"""
    print("\n" + "=" * 60)
    print("示例1：日线数据管道")
    print("=" * 60)

    pipeline = DataPipeline(output_dir="data_output/example1")

    # 添加股票
    pipeline.add_stocks(["600000", "000001", "600519"])

    # 运行管道
    pipeline.run_full_pipeline(start_date="2024-01-01", end_date="2024-12-31")


def example_batch_pipeline():
    """示例2：批量数据管道"""
    print("\n" + "=" * 60)
    print("示例2：批量数据管道")
    print("=" * 60)

    pipeline = DataPipeline(output_dir="data_output/example2")

    # 批量添加股票
    stocks = ["600000", "000001", "600519", "000858", "600036", "601318", "000333", "002415"]

    pipeline.add_stocks(stocks)

    # 运行管道（近3个月数据）
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    pipeline.run_full_pipeline(start_date=start_date, end_date=end_date)


def example_incremental_pipeline():
    """示例3：增量数据更新"""
    print("\n" + "=" * 60)
    print("示例3：增量数据更新")
    print("=" * 60)

    pipeline = DataPipeline(output_dir="data_output/example3")

    pipeline.add_stocks(["600000", "000001"])

    # 第一次运行：获取历史数据
    print("\n第一次运行（历史数据）：")
    pipeline.run_full_pipeline(start_date="2024-01-01", end_date="2024-10-31")

    # 第二次运行：增量更新
    print("\n第二次运行（增量更新）：")
    pipeline.run_full_pipeline(start_date="2024-11-01", end_date="2024-12-31")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("数据管道示例")
    print("=" * 60)

    # 运行示例
    example_daily_pipeline()
    example_batch_pipeline()
    example_incremental_pipeline()

    print("\n" + "=" * 60)
    print("所有示例运行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
