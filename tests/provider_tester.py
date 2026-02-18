#!/usr/bin/env python3
"""
Provider 接口测试工具

测试所有数据 Provider 的接口可用性和字段标准化功能。
"""

import json
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


class ProviderTester:
    """Provider 接口测试器"""

    def __init__(self, output_dir: str = "tests/results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.test_results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": [],
        }

        self._providers = self._discover_providers()

    def _discover_providers(self) -> dict[str, dict[str, Any]]:
        """发现所有可用的 Provider"""
        providers = {}

        modules_dir = os.path.join(PROJECT_ROOT, "src", "akshare_one", "modules")

        for module_name in os.listdir(modules_dir):
            module_path = os.path.join(modules_dir, module_name)
            if not os.path.isdir(module_path):
                continue

            factory_path = os.path.join(module_path, "factory.py")
            if not os.path.exists(factory_path):
                continue

            try:
                module = __import__(
                    f"akshare_one.modules.{module_name}.factory",
                    fromlist=[],
                )

                factory_class_name = None
                for attr in dir(module):
                    if attr.endswith("Factory") and attr != "Factory":
                        factory_class_name = attr
                        break

                if factory_class_name:
                    factory_class = getattr(module, factory_class_name)
                    if hasattr(factory_class, "get_provider"):
                        sources = []
                        if hasattr(factory_class, "list_sources"):
                            sources = factory_class.list_sources()

                        providers[module_name] = {
                            "module": module,
                            "factory": factory_class,
                            "sources": sources,
                        }
            except Exception as e:
                print(f"  跳过模块 {module_name}: {e}")

        return providers

    def get_available_providers(self) -> list[str]:
        """获取可用的 Provider 列表"""
        return list(self._providers.keys())

    def test_provider_basic(self, module_name: str, timeout: int = 30) -> dict[str, Any]:
        """
        测试单个 Provider 的基本功能

        Args:
            module_name: 模块名称
            timeout: 超时时间（秒）

        Returns:
            测试结果
        """
        result = {
            "module": module_name,
            "success": False,
            "error": None,
            "duration": 0,
            "field_types_inferred": {},
            "amount_fields_inferred": {},
            "data_shape": None,
            "columns": [],
        }

        if module_name not in self._providers:
            result["error"] = f"模块 {module_name} 不存在"
            return result

        start_time = time.time()

        try:
            provider_info = self._providers[module_name]
            factory_class = provider_info["factory"]
            sources = provider_info.get("sources", ["eastmoney"])

            source = "eastmoney" if "eastmoney" in sources else (sources[0] if sources else None)

            if source is None:
                result["error"] = "没有可用的数据源"
                return result

            provider = factory_class.get_provider(source)

            if provider is None:
                result["error"] = "Provider 实例化失败"
                return result

            try:
                raw_df = provider.fetch_data()
                if raw_df is not None and not raw_df.empty:
                    result["field_types_inferred"] = {
                        k: v.value for k, v in provider.infer_field_types(raw_df).items()
                    }
                    result["amount_fields_inferred"] = provider.infer_amount_fields(raw_df)
            except Exception:
                pass

            df = provider.get_data()

            if df is None:
                result["error"] = "返回值为 None"
                return result

            if isinstance(df, pd.DataFrame):
                result["data_shape"] = df.shape
                result["columns"] = list(df.columns)
                result["success"] = True
            elif isinstance(df, dict):
                result["data_shape"] = {"type": "dict", "keys": list(df.keys())}
                result["columns"] = list(df.keys())
                result["success"] = True
            else:
                result["data_shape"] = {"type": str(type(df))}
                result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
        finally:
            result["duration"] = round(time.time() - start_time, 3)

        return result

    def test_all_providers(
        self,
        modules: list[str] | None = None,
        parallel: bool = False,
        max_workers: int = 4,
    ) -> dict[str, Any]:
        """
        测试所有 Provider

        Args:
            modules: 指定要测试的模块列表，None 表示测试全部
            parallel: 是否并行测试
            max_workers: 并行测试的最大工作线程数

        Returns:
            测试结果汇总
        """
        test_modules = modules if modules else list(self._providers.keys())

        print(f"{'=' * 80}")
        print(f"开始测试 Provider 接口，共 {len(test_modules)} 个模块")
        print(f"{'=' * 80}")

        self.test_results = {
            "total": len(test_modules),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": [],
            "by_module": {},
        }

        if parallel:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.test_provider_basic, module): module
                    for module in test_modules
                }

                for future in as_completed(futures):
                    module = futures[future]
                    try:
                        result = future.result(timeout=60)
                        self._process_result(result)
                    except Exception as e:
                        result = {
                            "module": module,
                            "success": False,
                            "error": str(e),
                            "duration": 0,
                        }
                        self._process_result(result)
        else:
            for idx, module in enumerate(test_modules, 1):
                print(f"\n[{idx}/{len(test_modules)}] 测试: {module}")
                result = self.test_provider_basic(module)
                self._process_result(result)

        self._save_results()
        self._print_summary()

        return self.test_results

    def _process_result(self, result: dict[str, Any]):
        """处理单个测试结果"""
        self.test_results["details"].append(result)
        self.test_results["by_module"][result["module"]] = result

        if result["success"]:
            self.test_results["success"] += 1
            print(f"  ✓ 成功! 耗时: {result['duration']}s, 数据形状: {result['data_shape']}")
            if result.get("field_types_inferred"):
                print(f"    推断字段类型: {len(result['field_types_inferred'])} 个")
        else:
            self.test_results["failed"] += 1
            error_msg = result.get("error", "未知错误")
            print(f"  ✗ 失败: {error_msg[:100]}")

    def _save_results(self):
        """保存测试结果"""
        json_path = os.path.join(self.output_dir, "provider_test_results.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 详细结果已保存到: {json_path}")

        summary_data = []
        for detail in self.test_results["details"]:
            summary_data.append(
                {
                    "模块": detail["module"],
                    "是否成功": "成功" if detail["success"] else "失败",
                    "耗时(s)": detail["duration"],
                    "数据形状": str(detail.get("data_shape", "")),
                    "字段数": len(detail.get("columns", [])),
                    "推断字段类型数": len(detail.get("field_types_inferred", {})),
                    "推断金额字段数": len(detail.get("amount_fields_inferred", {})),
                    "错误信息": detail.get("error", ""),
                }
            )

        df = pd.DataFrame(summary_data)
        csv_path = os.path.join(self.output_dir, "provider_test_summary.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"✓ 汇总表已保存到: {csv_path}")

    def _print_summary(self):
        """打印测试汇总"""
        print("\n" + "=" * 80)
        print("测试汇总")
        print("=" * 80)
        print(f"  总模块数: {self.test_results['total']}")
        print(f"  成功: {self.test_results['success']}")
        print(f"  失败: {self.test_results['failed']}")

        if self.test_results["total"] > 0:
            success_rate = self.test_results["success"] / self.test_results["total"] * 100
            print(f"  成功率: {success_rate:.1f}%")

        if self.test_results["failed"] > 0:
            print("\n失败的模块:")
            for detail in self.test_results["details"]:
                if not detail["success"]:
                    print(f"  - {detail['module']}: {detail.get('error', '未知错误')[:80]}")

        print("\n" + "=" * 80)


def test_field_standardization():
    """测试字段标准化功能"""
    print("\n" + "=" * 80)
    print("测试字段标准化功能")
    print("=" * 80)

    from akshare_one.modules.field_naming.models import FIELD_EQUIVALENTS

    print(f"\n1. FIELD_EQUIVALENTS 字典包含 {len(FIELD_EQUIVALENTS)} 个标准字段")

    test_fields = [
        "日期",
        "DATE",
        "收盘价",
        "CLOSE",
        "成交量",
        "VOLUME",
        "代码",
        "symbol",
    ]

    print("\n2. 测试字段等价关系:")
    for field in test_fields:
        found = False
        for standard, equivalents in FIELD_EQUIVALENTS.items():
            if field in equivalents or field.lower() in [e.lower() for e in equivalents]:
                print(f"  {field} -> {standard}")
                found = True
                break
        if not found:
            print(f"  {field} -> 未找到映射")

    print("\n" + "=" * 80)


def test_formatter():
    """测试字段格式化功能"""
    from akshare_one.modules.field_naming.formatter import (
        DateFormat,
        FieldFormatter,
        StockCodeFormat,
    )

    print("\n" + "=" * 80)
    print("测试字段格式化功能")
    print("=" * 80)

    print("\n1. 股票代码格式化:")
    test_codes = ["000001", "000001.SZ", "sz000001", "600000.SH", "sh600000"]
    for code in test_codes:
        pure = FieldFormatter.normalize_stock_code(code, StockCodeFormat.PURE_NUMERIC)
        with_suffix = FieldFormatter.normalize_stock_code(code, StockCodeFormat.WITH_SUFFIX)
        print(f"  {code:15} -> 纯数字: {pure:8} 带后缀: {with_suffix or '-':12}")

    print("\n2. 日期格式化:")
    test_dates = ["20240101", "2024-01-01", "2024年1月1日", "2024/01/01"]
    for date in test_dates:
        formatted = FieldFormatter.normalize_date(date, DateFormat.YYYY_MM_DD)
        print(f"  {date:20} -> {formatted}")

    print("\n3. 数值格式化:")
    test_values = ["123.45", "1,234.56", "100%", "-78.9"]
    for val in test_values:
        formatted = FieldFormatter.normalize_float(val)
        print(f"  {val:15} -> {formatted}")

    print("\n" + "=" * 80)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Provider 接口测试工具")
    parser.add_argument("--test-all", action="store_true", help="测试所有 Provider")
    parser.add_argument("--test-modules", help="测试指定模块（逗号分隔）")
    parser.add_argument("--test-standardization", action="store_true", help="测试字段标准化")
    parser.add_argument("--test-formatter", action="store_true", help="测试字段格式化")
    parser.add_argument("--parallel", action="store_true", help="并行测试")
    parser.add_argument("--output-dir", default="tests/results", help="输出目录")

    args = parser.parse_args()

    if args.test_standardization:
        test_field_standardization()

    if args.test_formatter:
        test_formatter()

    if args.test_all or args.test_modules:
        tester = ProviderTester(output_dir=args.output_dir)

        modules = None
        if args.test_modules:
            modules = [m.strip() for m in args.test_modules.split(",")]

        tester.test_all_providers(modules=modules, parallel=args.parallel)

    if not any([args.test_all, args.test_modules, args.test_standardization, args.test_formatter]):
        print("=" * 80)
        print("Provider 接口测试工具")
        print("=" * 80)
        print("\n使用方式:")
        print("  测试所有接口:   python provider_tester.py --test-all")
        print("  测试指定模块:   python provider_tester.py --test-modules fundflow,northbound")
        print("  测试标准化:     python provider_tester.py --test-standardization")
        print("  测试格式化:     python provider_tester.py --test-formatter")
        print("  并行测试:       python provider_tester.py --test-all --parallel")

        print("\n先测试字段标准化和格式化功能...")
        test_field_standardization()
        test_formatter()


if __name__ == "__main__":
    main()
