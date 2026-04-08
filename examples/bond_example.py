#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可转债示例：获取可转债数据

本示例展示如何使用 akshare-one 获取可转债数据，包括：
- 获取可转债列表

运行方式：
    python examples/bond_example.py
"""

import pandas as pd
from akshare_one import get_bond_list


def example_bond_list():
    """示例1：获取可转债列表"""
    print("\n" + "=" * 60)
    print("示例1：获取可转债列表")
    print("=" * 60)

    df = get_bond_list(source="jsl")

    print(f"\n获取到 {len(df)} 只可转债")
    if not df.empty:
        print("\n前10只可转债：")
        print(df.head(10).to_string(index=False))


def main():
    """运行所有示例"""
    print("=" * 60)
    print("akshare-one 可转债数据获取示例")
    print("=" * 60)

    example_bond_list()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
