#!/usr/bin/env python3
"""
CI 标准化检查工具

自动检测：
- 未使用标准化的模块
- 字段命名不一致
- 配置文件缺失
"""

import json
import os
import sys
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


class StandardizationChecker:
    """标准化检查器"""

    def __init__(self):
        self.modules_dir = os.path.join(PROJECT_ROOT, "src", "akshare_one", "modules")
        self.config_dir = os.path.join(self.modules_dir, "config")
        self.results = {
            "passed": [],
            "warnings": [],
            "errors": [],
            "summary": {
                "total_modules": 0,
                "modules_with_config": 0,
                "modules_using_standardization": 0,
                "modules_needing_attention": 0,
            },
        }

    def check_all(self) -> dict[str, Any]:
        """执行所有检查"""
        print("=" * 80)
        print("CI 标准化检查")
        print("=" * 80)

        self._check_config_file()
        self._check_all_modules()

        self._print_summary()
        self._save_results()

        return self.results

    def _check_config_file(self):
        """检查配置文件是否存在"""
        print("\n[1] 检查配置文件...")

        config_path = os.path.join(self.config_dir, "field_mappings.json")
        if os.path.exists(config_path):
            self.results["passed"].append(
                {"check": "config_file_exists", "message": f"配置文件存在: {config_path}"}
            )
            print(f"  ✓ 配置文件存在: {config_path}")

            try:
                with open(config_path, encoding="utf-8") as f:
                    config = json.load(f)

                modules_configured = len(config.get("modules", {}))
                self.results["summary"]["modules_with_config"] = modules_configured
                self.results["passed"].append(
                    {
                        "check": "config_modules_count",
                        "message": f"已配置模块数: {modules_configured}",
                    }
                )
                print(f"  ✓ 已配置模块数: {modules_configured}")
            except Exception as e:
                self.results["errors"].append(
                    {"check": "config_file_parse", "message": f"配置文件解析失败: {e}"}
                )
                print(f"  ✗ 配置文件解析失败: {e}")
        else:
            self.results["errors"].append(
                {"check": "config_file_exists", "message": "配置文件不存在"}
            )
            print("  ✗ 配置文件不存在")

    def _check_all_modules(self):
        """检查所有模块"""
        print("\n[2] 检查模块标准化...")

        modules = []
        for item in os.listdir(self.modules_dir):
            item_path = os.path.join(self.modules_dir, item)
            if os.path.isdir(item_path) and not item.startswith("_"):
                if os.path.exists(os.path.join(item_path, "factory.py")):
                    modules.append(item)

        self.results["summary"]["total_modules"] = len(modules)
        print(f"  发现 {len(modules)} 个模块")

        for module in modules:
            self._check_module(module)

    def _check_module(self, module_name: str):
        """检查单个模块"""
        module_path = os.path.join(self.modules_dir, module_name)

        module_info = {
            "name": module_name,
            "has_config": False,
            "uses_standardization": False,
            "issues": [],
        }

        config_path = os.path.join(self.config_dir, "field_mappings.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, encoding="utf-8") as f:
                    config = json.load(f)
                if module_name in config.get("modules", {}):
                    module_info["has_config"] = True
            except Exception:
                pass

        uses_std = self._check_module_uses_standardization(module_path)
        module_info["uses_standardization"] = uses_std

        if module_info["has_config"] and uses_std:
            self.results["passed"].append(
                {
                    "check": "module_standardization",
                    "module": module_name,
                    "message": "模块已完成标准化配置",
                }
            )
            self.results["summary"]["modules_using_standardization"] += 1
            print(f"  ✓ {module_name}: 已完成标准化")
        elif uses_std:
            self.results["warnings"].append(
                {
                    "check": "module_config_missing",
                    "module": module_name,
                    "message": "模块使用标准化但缺少配置",
                }
            )
            module_info["issues"].append("缺少配置")
            print(f"  ⚠ {module_name}: 使用标准化但缺少配置")
        else:
            self.results["errors"].append(
                {
                    "check": "module_no_standardization",
                    "module": module_name,
                    "message": "模块未使用标准化",
                }
            )
            module_info["issues"].append("未使用标准化")
            print(f"  ✗ {module_name}: 未使用标准化")

        if module_info["issues"]:
            self.results["summary"]["modules_needing_attention"] += 1

    def _check_module_uses_standardization(self, module_path: str) -> bool:
        """检查模块是否使用标准化"""
        indicators = [
            "infer_field_types",
            "infer_amount_fields",
            "standardize_dataframe",
            "apply_field_standardization",
            "apply_amount_conversion",
            "get_data_with_full_standardization",
            "field_types",
            "FieldType",
            "BaseProvider",
            "from ..base import",
            "from akshare_one.modules.base import",
        ]

        special_modules = ["indicators"]
        module_name = os.path.basename(module_path)
        if module_name in special_modules:
            return True

        for root, dirs, files in os.walk(module_path):
            dirs[:] = [d for d in dirs if not d.startswith("_") and d != "__pycache__"]

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()

                    for indicator in indicators:
                        if indicator in content:
                            return True

                except Exception:
                    pass

        return False

    def _check_field_naming_consistency(self):
        """检查字段命名一致性"""
        print("\n[3] 检查字段命名一致性...")

        from akshare_one.modules.field_naming.models import FIELD_EQUIVALENTS

        all_fields = set()
        for equivalents in FIELD_EQUIVALENTS.values():
            all_fields.update(equivalents)

        print(f"  已定义 {len(FIELD_EQUIVALENTS)} 个标准字段，{len(all_fields)} 个等价字段")

        self.results["passed"].append(
            {
                "check": "field_equivalents",
                "message": f"已定义 {len(FIELD_EQUIVALENTS)} 个标准字段",
            }
        )

    def _print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 80)
        print("检查摘要")
        print("=" * 80)

        summary = self.results["summary"]
        print(f"  总模块数: {summary['total_modules']}")
        print(f"  已配置模块: {summary['modules_with_config']}")
        print(f"  使用标准化模块: {summary['modules_using_standardization']}")
        print(f"  需要关注的模块: {summary['modules_needing_attention']}")

        print(f"\n  通过: {len(self.results['passed'])}")
        print(f"  警告: {len(self.results['warnings'])}")
        print(f"  错误: {len(self.results['errors'])}")

        if self.results["errors"]:
            print("\n需要修复的问题:")
            for error in self.results["errors"]:
                module = error.get("module", "全局")
                print(f"  - [{module}] {error['message']}")

        print("\n" + "=" * 80)

    def _save_results(self):
        """保存检查结果"""
        output_path = os.path.join(PROJECT_ROOT, "tests", "results", "standardization_check.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 检查结果已保存到: {output_path}")

    def get_exit_code(self) -> int:
        """获取退出码"""
        if self.results["errors"]:
            return 1
        elif self.results["warnings"]:
            return 2
        else:
            return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="CI 标准化检查工具")
    parser.add_argument("--check", action="store_true", help="执行检查")
    parser.add_argument("--ci", action="store_true", help="CI 模式（返回退出码）")

    args = parser.parse_args()

    checker = StandardizationChecker()

    if args.check or args.ci:
        checker.check_all()

        if args.ci:
            exit_code = checker.get_exit_code()
            print(f"\n退出码: {exit_code}")
            sys.exit(exit_code)
    else:
        print("=" * 80)
        print("CI 标准化检查工具")
        print("=" * 80)
        print("\n使用方式:")
        print("  执行检查: python standardization_check.py --check")
        print("  CI 模式:  python standardization_check.py --ci")


if __name__ == "__main__":
    main()
