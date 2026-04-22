from typing import Any
import pandas as pd
from .base import AnalysisFactory
from . import akshare as akshare_provider


def analyze_share_change_trend(
    symbol: str,
    period_days: int = 90,
    source: str | None = None,
) -> dict:
    """分析股东变动趋势

    根据近期股东户数变化判断筹码集中度趋势。

    Args:
        symbol: 股票代码
        period_days: 分析周期(天)

    Returns:
        dict: 分析结果
        - signal: 信号 (concentrating/dispersing/neutral)
        - holder_change_pct: 股东户数变化比例(%)
        - trend: 趋势描述
        - periods_analyzed: 分析的期数
    """
    from ..providers.equities.corporate_events.shareholder import get_latest_holder_number

    try:
        df = get_latest_holder_number(symbol)
        if df.empty or len(df) < 2:
            return {
                "signal": "neutral",
                "holder_change_pct": 0,
                "trend": "数据不足",
                "periods_analyzed": 0,
            }

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        latest_count = latest.get("股东户数", latest.get("holder_count", 0))
        prev_count = prev.get("股东户数", prev.get("holder_count", 0))

        if prev_count == 0:
            change_pct = 0
        else:
            change_pct = (latest_count - prev_count) / prev_count * 100

        if change_pct < -5:
            signal = "concentrating"
            trend = "筹码明显集中"
        elif change_pct < -1:
            signal = "concentrating"
            trend = "筹码小幅集中"
        elif change_pct > 5:
            signal = "dispersing"
            trend = "筹码明显分散"
        elif change_pct > 1:
            signal = "dispersing"
            trend = "筹码小幅分散"
        else:
            signal = "neutral"
            trend = "筹码稳定"

        return {
            "signal": signal,
            "holder_change_pct": round(change_pct, 2),
            "trend": trend,
            "periods_analyzed": len(df),
        }
    except Exception as e:
        return {
            "signal": "unknown",
            "holder_change_pct": 0,
            "trend": f"分析失败: {str(e)}",
            "periods_analyzed": 0,
        }


def analyze_unlock_impact(
    symbol: str,
    days_ahead: int = 30,
    source: str | None = None,
) -> dict:
    """分析解禁压力

    评估近期解禁对股价的潜在影响。

    Args:
        symbol: 股票代码
        days_ahead: 未来天数

    Returns:
        dict: 分析结果
        - risk_level: 风险等级 (high/medium/low/none)
        - unlock_shares: 解禁股数
        - unlock_value: 解禁市值(元)
        - float_ratio: 占流通盘比例(%)
        - unlock_date: 最近解禁日期
        - description: 描述
    """
    from ..providers.equities.corporate_events.restricted import get_restricted_release

    try:
        from datetime import datetime, timedelta

        start = datetime.now().strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

        df = get_restricted_release(symbol, start_date=start, end_date=end)

        if df.empty:
            return {
                "risk_level": "none",
                "unlock_shares": 0,
                "unlock_value": 0,
                "float_ratio": 0,
                "unlock_date": None,
                "description": f"未来{days_ahead}天内无解禁",
            }

        unlock_shares = df["解禁股数"].sum() if "解禁股数" in df.columns else 0
        unlock_value = df["解禁市值"].sum() if "解禁市值" in df.columns else 0
        float_ratio = df["占总股本比例"].sum() if "占总股本比例" in df.columns else 0

        if float_ratio > 30 or unlock_value > 10_000_000_000:
            risk_level = "high"
            desc = "大规模解禁，压力较大"
        elif float_ratio > 10 or unlock_value > 1_000_000_000:
            risk_level = "medium"
            desc = "中等规模解禁，关注压力"
        else:
            risk_level = "low"
            desc = "小规模解禁，影响有限"

        unlock_date = df.iloc[0].get("解禁日期", df.iloc[0].get("date", ""))

        return {
            "risk_level": risk_level,
            "unlock_shares": int(unlock_shares),
            "unlock_value": float(unlock_value),
            "float_ratio": round(float(float_ratio), 2),
            "unlock_date": str(unlock_date),
            "description": desc,
        }
    except Exception as e:
        return {
            "risk_level": "unknown",
            "unlock_shares": 0,
            "unlock_value": 0,
            "float_ratio": 0,
            "unlock_date": None,
            "description": f"分析失败: {str(e)}",
        }


__all__ = ["analyze_share_change_trend", "analyze_unlock_impact", "AnalysisFactory"]
