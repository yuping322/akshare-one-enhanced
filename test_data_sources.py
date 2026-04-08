#!/usr/bin/env python3
"""测试各个数据源的可用性"""

import time
from akshare_one import get_hist_data, get_hist_data_multi_source


def test_historical_sources():
    """测试历史数据源的可用性"""
    sources = ["eastmoney", "eastmoney_direct", "sina", "tencent", "netease", "lixinger"]
    symbol = "600000"

    print("=" * 60)
    print("测试历史数据源可用性")
    print("=" * 60)

    results = {}
    for source in sources:
        try:
            start = time.time()
            df = get_hist_data(symbol=symbol, start_date="2024-01-01", end_date="2024-01-31", source=source)
            elapsed = time.time() - start

            if df is not None and len(df) > 0:
                results[source] = {"status": "✓ 可用", "rows": len(df), "time": f"{elapsed:.2f}s"}
                print(f"{source:20s} ✓ 可用 - {len(df)} 行数据 - {elapsed:.2f}s")
            else:
                results[source] = {"status": "✗ 无数据", "rows": 0, "time": f"{elapsed:.2f}s"}
                print(f"{source:20s} ✗ 无数据")
        except Exception as e:
            error_msg = str(e)[:50]
            results[source] = {"status": "✗ 错误", "error": error_msg}
            print(f"{source:20s} ✗ 错误: {error_msg}")

    print("\n" + "=" * 60)
    print("测试多数据源自动切换")
    print("=" * 60)

    try:
        start = time.time()
        df = get_hist_data_multi_source(
            symbol=symbol,
            start_date="2024-01-01",
            end_date="2024-01-31",
            sources=["eastmoney_direct", "eastmoney", "sina", "tencent", "netease"],
        )
        elapsed = time.time() - start
        actual_source = df.attrs.get("source", "unknown")

        if df is not None and len(df) > 0:
            print(f"✓ 成功获取数据 - 使用数据源: {actual_source} - {len(df)} 行 - {elapsed:.2f}s")
        else:
            print("✗ 未获取到数据")
    except Exception as e:
        print(f"✗ 多数据源失败: {str(e)[:100]}")

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    available = [s for s, r in results.items() if "✓" in r["status"]]
    unavailable = [s for s, r in results.items() if "✗" in r["status"]]

    print(f"\n可用数据源 ({len(available)}): {', '.join(available)}")
    print(f"不可用数据源 ({len(unavailable)}): {', '.join(unavailable)}")

    return results


if __name__ == "__main__":
    test_historical_sources()
