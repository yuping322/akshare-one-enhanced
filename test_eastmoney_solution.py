#!/usr/bin/env python3
"""
东方财富 API 问题解决方案测试脚本

使用方法:
1. 方案1: 使用 sina/lixinger 数据源（无需额外配置）
   python test_eastmoney_solution.py --method=switch-source

2. 方案2: 安装 akshare-proxy-patch
   pip install akshare-proxy-patch
   python test_eastmoney_solution.py --method=proxy-patch --token=YOUR_TOKEN

3. 方案3: 多数据源自动切换
   python test_eastmoney_solution.py --method=multi-source
"""

import argparse
import sys
import time


def test_switch_source():
    """方案1: 切换到可用数据源"""
    print("=" * 80)
    print("方案1: 使用 sina/lixinger 数据源")
    print("=" * 80)

    from akshare_one import get_hist_data

    symbol = "600000"

    # 测试 sina
    print("\n测试 sina 数据源...")
    try:
        start = time.time()
        df = get_hist_data(symbol=symbol, start_date="2024-01-01", end_date="2024-01-31", source="sina")
        elapsed = time.time() - start
        if df is not None and not df.empty:
            print(f"✓ sina 可用 - {len(df)} 行数据 - {elapsed:.2f}s")
            print(f"  数据示例: {df.iloc[0].to_dict()}")
        else:
            print("✗ sina 返回空数据")
    except Exception as e:
        print(f"✗ sina 失败: {str(e)[:100]}")

    # 测试 lixinger
    print("\n测试 lixinger 数据源...")
    try:
        start = time.time()
        df = get_hist_data(symbol=symbol, start_date="2024-01-01", end_date="2024-01-31", source="lixinger")
        elapsed = time.time() - start
        if df is not None and not df.empty:
            print(f"✓ lixinger 可用 - {len(df)} 行数据 - {elapsed:.2f}s")
            print(f"  数据示例: {df.iloc[0].to_dict()}")
        else:
            print("✗ lixinger 返回空数据")
    except Exception as e:
        print(f"✗ lixinger 失败: {str(e)[:100]}")

    print("\n建议: 在代码中使用 source='sina' 或 source='lixinger'")


def test_proxy_patch(token=None):
    """方案2: 使用 akshare-proxy-patch"""
    print("=" * 80)
    print("方案2: 使用 akshare-proxy-patch")
    print("=" * 80)

    if not token:
        print("\n错误: 需要提供 TOKEN")
        print("获取 TOKEN: https://ak.cheapproxy.net/dashboard/akshare")
        return

    try:
        import akshare_proxy_patch

        print("\n安装 akshare-proxy-patch 补丁...")
        akshare_proxy_patch.install_patch(
            "101.201.173.125",
            auth_token=token,
            retry=30,
            hook_domains=[
                "push2his.eastmoney.com",
                "push2.eastmoney.com",
                "emweb.securities.eastmoney.com",
            ],
        )
        print("✓ 补丁安装成功")

        from akshare_one import get_hist_data

        print("\n测试 eastmoney 数据源（使用代理补丁）...")
        symbol = "600000"
        start = time.time()
        try:
            df = get_hist_data(symbol=symbol, start_date="2024-01-01", end_date="2024-01-31", source="eastmoney")
            elapsed = time.time() - start
            if df is not None and not df.empty:
                print(f"✓ eastmoney 可用（通过代理） - {len(df)} 行数据 - {elapsed:.2f}s")
                print(f"  数据示例: {df.iloc[0].to_dict()}")
            else:
                print("✗ eastmoney 返回空数据")
        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ eastmoney 失败 ({elapsed:.2f}s): {str(e)[:100]}")

    except ImportError:
        print("\n错误: 未安装 akshare-proxy-patch")
        print("安装命令: pip install akshare-proxy-patch==0.2.13")
        return
    except Exception as e:
        print(f"\n错误: {str(e)[:100]}")
        return


def test_multi_source():
    """方案3: 多数据源自动切换"""
    print("=" * 80)
    print("方案3: 多数据源自动切换")
    print("=" * 80)

    from akshare_one import get_hist_data_multi_source

    symbol = "600000"

    print("\n测试自动切换（优先使用可用数据源）...")
    start = time.time()
    try:
        # 优先级: sina > lixinger > eastmoney_direct > eastmoney
        df = get_hist_data_multi_source(
            symbol=symbol,
            start_date="2024-01-01",
            end_date="2024-01-31",
            sources=["sina", "lixinger", "eastmoney_direct", "eastmoney"],
        )
        elapsed = time.time() - start

        actual_source = df.attrs.get("source", "unknown")
        if df is not None and not df.empty:
            print(f"✓ 成功获取数据")
            print(f"  实际使用数据源: {actual_source}")
            print(f"  数据条数: {len(df)}")
            print(f"  响应时间: {elapsed:.2f}s")
            print(f"  数据示例: {df.iloc[0].to_dict()}")
        else:
            print("✗ 返回空数据")
    except Exception as e:
        elapsed = time.time() - start
        print(f"✗ 失败 ({elapsed:.2f}s): {str(e)[:100]}")

    print("\n建议: 使用 get_hist_data_multi_source() 自动切换到可用数据源")


def main():
    parser = argparse.ArgumentParser(description="测试东方财富 API 问题解决方案")
    parser.add_argument(
        "--method",
        choices=["switch-source", "proxy-patch", "multi-source"],
        default="multi-source",
        help="解决方案类型",
    )
    parser.add_argument("--token", help="akshare-proxy-patch 的 TOKEN（仅用于 proxy-patch 方法）")

    args = parser.parse_args()

    print("\n东方财富 API 问题解决方案测试")
    print("=" * 80)

    if args.method == "switch-source":
        test_switch_source()
    elif args.method == "proxy-patch":
        test_proxy_patch(args.token)
    elif args.method == "multi-source":
        test_multi_source()

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
    print("\n详细解决方案文档: EASTMONEY_API_ISSUE.md")


if __name__ == "__main__":
    main()
