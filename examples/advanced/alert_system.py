#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级示例 3：预警系统

本示例展示如何使用 akshare-one 构建简单的预警系统，包括：
- 实时监控股票价格
- 设置预警条件
- 触发预警通知

运行方式：
    python examples/advanced/alert_system.py

注意：本示例仅供学习参考，实际应用需要更完善的架构
"""

import time
from datetime import datetime
from akshare_one import get_realtime_data, get_hist_data


class AlertSystem:
    """股票预警系统"""

    def __init__(self):
        self.alert_rules = []
        self.alert_history = []

    def add_price_alert(self, symbol, target_price, condition="above"):
        """
        添加价格预警

        Args:
            symbol: 股票代码
            target_price: 目标价格
            condition: 条件 ('above' 或 'below')
        """
        rule = {
            "symbol": symbol,
            "type": "price",
            "target_price": target_price,
            "condition": condition,
            "enabled": True,
        }
        self.alert_rules.append(rule)
        print(f"已添加价格预警: {symbol} {condition} {target_price}")

    def add_change_alert(self, symbol, pct_threshold, condition="above"):
        """
        添加涨跌幅预警

        Args:
            symbol: 股票代码
            pct_threshold: 涨跌幅阈值
            condition: 条件 ('above' 或 'below')
        """
        rule = {
            "symbol": symbol,
            "type": "change",
            "pct_threshold": pct_threshold,
            "condition": condition,
            "enabled": True,
        }
        self.alert_rules.append(rule)
        print(f"已添加涨跌幅预警: {symbol} {condition} {pct_threshold}%")

    def add_volume_alert(self, symbol, volume_multiplier=2):
        """
        添加成交量预警

        Args:
            symbol: 股票代码
            volume_multiplier: 成交量倍数（相对于平均成交量）
        """
        # 首先获取历史平均成交量
        try:
            df = get_hist_data(
                symbol=symbol, interval="day", start_date="2024-01-01", end_date="2024-12-31", source="eastmoney_direct"
            )
            avg_volume = df["volume"].mean() if not df.empty else 0
        except (ValueError, ConnectionError) as e:
            print(f"警告: 获取历史数据失败 ({symbol}): {e}")
            print("将使用默认成交量阈值")
            avg_volume = 0

        rule = {
            "symbol": symbol,
            "type": "volume",
            "avg_volume": avg_volume,
            "volume_multiplier": volume_multiplier,
            "enabled": True,
        }
        self.alert_rules.append(rule)
        print(f"已添加成交量预警: {symbol} 成交量超过 {volume_multiplier}倍均量")

    def check_alerts(self):
        """检查所有预警规则"""
        alerts_triggered = []

        for rule in self.alert_rules:
            if not rule["enabled"]:
                continue

            symbol = rule["symbol"]

            try:
                # 获取实时数据
                df = get_realtime_data(symbol=symbol, source="eastmoney_direct")

                if df.empty:
                    continue

                latest = df.iloc[0]

                # 检查价格预警
                if rule["type"] == "price":
                    current_price = latest["price"]
                    target_price = rule["target_price"]

                    if rule["condition"] == "above" and current_price >= target_price:
                        alert_msg = (
                            f"[价格预警] {symbol} 当前价格 {current_price:.2f} 已达到目标价格 {target_price:.2f}"
                        )
                        alerts_triggered.append(alert_msg)

                    elif rule["condition"] == "below" and current_price <= target_price:
                        alert_msg = (
                            f"[价格预警] {symbol} 当前价格 {current_price:.2f} 已跌破目标价格 {target_price:.2f}"
                        )
                        alerts_triggered.append(alert_msg)

                # 检查涨跌幅预警
                elif rule["type"] == "change":
                    pct_change = latest["pct_change"]
                    pct_threshold = rule["pct_threshold"]

                    if rule["condition"] == "above" and pct_change >= pct_threshold:
                        alert_msg = f"[涨跌幅预警] {symbol} 当前涨幅 {pct_change:.2f}% 已超过阈值 {pct_threshold}%"
                        alerts_triggered.append(alert_msg)

                    elif rule["condition"] == "below" and pct_change <= pct_threshold:
                        alert_msg = f"[涨跌幅预警] {symbol} 当前跌幅 {pct_change:.2f}% 已跌破阈值 {pct_threshold}%"
                        alerts_triggered.append(alert_msg)

                # 检查成交量预警
                elif rule["type"] == "volume":
                    current_volume = latest["volume"]
                    avg_volume = rule["avg_volume"]
                    multiplier = rule["volume_multiplier"]

                    if current_volume >= avg_volume * multiplier:
                        alert_msg = f"[成交量预警] {symbol} 当前成交量 {current_volume:.0f}手 是均量 {avg_volume:.0f}手 的 {current_volume / avg_volume:.1f}倍"
                        alerts_triggered.append(alert_msg)

            except Exception as e:
                print(f"检查 {symbol} 时出错: {e}")

        return alerts_triggered

    def run_monitoring(self, interval_seconds=5, max_checks=10):
        """
        运行监控

        Args:
            interval_seconds: 检查间隔（秒）
            max_checks: 最大检查次数
        """
        print("\n" + "=" * 60)
        print("开始监控...")
        print("=" * 60)
        print(f"检查间隔: {interval_seconds}秒")
        print(f"预警规则数: {len(self.alert_rules)}")
        print("-" * 60)

        for i in range(max_checks):
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 第 {i + 1} 次检查")

            alerts = self.check_alerts()

            if alerts:
                print("\n触发预警：")
                for alert in alerts:
                    print(f"  ⚠️  {alert}")
                    self.alert_history.append({"time": datetime.now(), "alert": alert})

            if i < max_checks - 1:
                time.sleep(interval_seconds)

        print("\n监控结束")

    def show_alert_history(self):
        """显示预警历史"""
        if self.alert_history:
            print("\n预警历史：")
            print("-" * 60)
            for record in self.alert_history:
                print(f"  {record['time'].strftime('%Y-%m-%d %H:%M:%S')}: {record['alert']}")
        else:
            print("\n暂无预警记录")


def example_basic_alerts():
    """示例1：基础价格预警"""
    print("\n" + "=" * 60)
    print("示例1：基础价格预警")
    print("=" * 60)

    # 创建预警系统
    alert_system = AlertSystem()

    # 添加价格预警
    alert_system.add_price_alert("600000", 10.0, "above")  # 浦发银行突破10元
    alert_system.add_price_alert("000001", 15.0, "below")  # 平安银行跌破15元

    # 添加涨跌幅预警
    alert_system.add_change_alert("600519", 3.0, "above")  # 贵州茅台涨幅超过3%

    # 运行监控（演示3次）
    alert_system.run_monitoring(interval_seconds=5, max_checks=3)

    # 显示预警历史
    alert_system.show_alert_history()


def example_volume_alert():
    """示例2：成交量预警"""
    print("\n" + "=" * 60)
    print("示例2：成交量预警")
    print("=" * 60)

    alert_system = AlertSystem()

    # 添加成交量预警（成交量超过2倍均量）
    alert_system.add_volume_alert("600000", volume_multiplier=2)

    # 运行监控
    alert_system.run_monitoring(interval_seconds=5, max_checks=3)


def example_combined_alerts():
    """示例3：组合预警"""
    print("\n" + "=" * 60)
    print("示例3：组合预警（价格+涨跌幅+成交量）")
    print("=" * 60)

    alert_system = AlertSystem()

    # 添加多种类型的预警
    alert_system.add_price_alert("600000", 10.5, "above")
    alert_system.add_change_alert("600000", 2.0, "above")
    alert_system.add_volume_alert("600000", volume_multiplier=1.5)

    alert_system.add_price_alert("000001", 12.0, "below")
    alert_system.add_change_alert("000001", -2.0, "below")

    # 运行监控
    alert_system.run_monitoring(interval_seconds=5, max_checks=5)

    # 显示预警历史
    alert_system.show_alert_history()


def main():
    """运行所有示例"""
    print("=" * 60)
    print("股票预警系统示例")
    print("=" * 60)
    print("\n注意：")
    print("- 本示例仅供学习参考")
    print("- 实际应用需要更完善的架构")
    print("- 建议使用消息队列和持久化存储")
    print("=" * 60)

    # 运行示例
    example_basic_alerts()
    example_volume_alert()
    example_combined_alerts()

    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
