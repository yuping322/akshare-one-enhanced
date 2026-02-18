#!/usr/bin/env python3
"""
数据字典生成工具

从 Provider 自动反射生成字段文档，包括：
- 字段名称
- 字段类型
- 字段描述
- 示例值
"""

import contextlib
import inspect
import json
import os
import sys
from collections import defaultdict
from typing import Any

import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


class DataDictionaryGenerator:
    """数据字典生成器"""

    def __init__(self, output_dir: str = "docs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self._providers = self._discover_providers()
        self._field_registry: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "modules": [],
                "types": set(),
                "descriptions": [],
                "examples": [],
            }
        )

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
            except Exception:
                pass

        return providers

    def get_available_providers(self) -> list[str]:
        """获取可用的 Provider 列表"""
        return list(self._providers.keys())

    def analyze_provider(self, module_name: str) -> dict[str, Any]:
        """
        分析单个 Provider 的字段信息

        Args:
            module_name: 模块名称

        Returns:
            字段信息字典
        """
        result = {
            "module": module_name,
            "success": False,
            "error": None,
            "fields": {},
            "methods": [],
            "config": {},
        }

        if module_name not in self._providers:
            result["error"] = f"模块 {module_name} 不存在"
            return result

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

            methods = []
            for name in dir(provider):
                if name.startswith("_"):
                    continue
                attr = getattr(provider, name)
                if callable(attr):
                    sig = None
                    with contextlib.suppress(Exception):
                        sig = str(inspect.signature(attr))
                    methods.append(
                        {
                            "name": name,
                            "signature": sig,
                            "doc": inspect.getdoc(attr) or "",
                        }
                    )
            result["methods"] = methods

            try:
                from akshare_one.modules.config import get_field_mapping_config

                config = get_field_mapping_config()
                result["config"] = {
                    "field_types": {
                        k: v.value for k, v in config.get_field_types(module_name).items()
                    },
                    "amount_fields": config.get_amount_fields(module_name),
                }
            except Exception:
                pass

            try:
                raw_df = provider.fetch_data()
                if raw_df is not None and not raw_df.empty:
                    field_types = provider.infer_field_types(raw_df)
                    amount_fields = provider.infer_amount_fields(raw_df)

                    for col in raw_df.columns:
                        result["fields"][col] = {
                            "dtype": str(raw_df[col].dtype),
                            "inferred_type": field_types.get(col, FieldType.OTHER).value
                            if field_types.get(col)
                            else "unknown",
                            "amount_unit": amount_fields.get(col),
                            "sample_values": self._get_sample_values(raw_df[col]),
                            "null_count": int(raw_df[col].isna().sum()),
                            "null_rate": round(raw_df[col].isna().sum() / len(raw_df) * 100, 2),
                        }
            except Exception as e:
                result["error"] = str(e)

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)

        return result

    def _get_sample_values(self, series: pd.Series, max_samples: int = 5) -> list:
        """获取字段的样本值"""
        samples = []
        for val in series.dropna().head(max_samples):
            if isinstance(val, (int, float, str, bool)):
                samples.append(val)
            else:
                samples.append(str(val))
        return samples

    def generate_all_dictionaries(self, modules: list[str] | None = None) -> dict[str, Any]:
        """
        生成所有模块的数据字典

        Args:
            modules: 指定模块列表，None 表示全部

        Returns:
            所有模块的数据字典
        """
        test_modules = modules if modules else list(self._providers.keys())

        print(f"{'=' * 80}")
        print(f"生成数据字典，共 {len(test_modules)} 个模块")
        print(f"{'=' * 80}")

        all_dictionaries = {
            "version": "1.0",
            "generated_at": pd.Timestamp.now().isoformat(),
            "modules": {},
            "field_index": {},
        }

        for idx, module in enumerate(test_modules, 1):
            print(f"\n[{idx}/{len(test_modules)}] 分析: {module}")
            result = self.analyze_provider(module)
            all_dictionaries["modules"][module] = result

            if result["success"]:
                print(f"  ✓ 成功! 字段数: {len(result['fields'])}")
                for field, info in result["fields"].items():
                    all_dictionaries["field_index"].setdefault(
                        field,
                        {"modules": [], "types": set(), "sample_values": []},
                    )
                    all_dictionaries["field_index"][field]["modules"].append(module)
                    all_dictionaries["field_index"][field]["types"].add(info["inferred_type"])
                    all_dictionaries["field_index"][field]["sample_values"].extend(
                        info["sample_values"]
                    )
            else:
                print(f"  ✗ 失败: {result.get('error', '未知错误')}")

        for field in all_dictionaries["field_index"]:
            all_dictionaries["field_index"][field]["types"] = list(
                all_dictionaries["field_index"][field]["types"]
            )
            all_dictionaries["field_index"][field]["sample_values"] = list(
                set(all_dictionaries["field_index"][field]["sample_values"][:10])
            )

        self._save_dictionaries(all_dictionaries)
        self._generate_markdown_docs(all_dictionaries)

        return all_dictionaries

    def _save_dictionaries(self, dictionaries: dict[str, Any]):
        """保存数据字典"""
        json_path = os.path.join(self.output_dir, "data_dictionary.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dictionaries, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 数据字典已保存到: {json_path}")

        rows = []
        for module, info in dictionaries["modules"].items():
            if not info.get("success"):
                continue
            for field, field_info in info.get("fields", {}).items():
                rows.append(
                    {
                        "模块": module,
                        "字段名": field,
                        "数据类型": field_info.get("dtype", ""),
                        "推断类型": field_info.get("inferred_type", ""),
                        "金额单位": field_info.get("amount_unit", ""),
                        "空值率(%)": field_info.get("null_rate", 0),
                        "示例值": str(field_info.get("sample_values", [])[:3]),
                    }
                )

        if rows:
            df = pd.DataFrame(rows)
            csv_path = os.path.join(self.output_dir, "data_dictionary.csv")
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            print(f"✓ CSV 字典已保存到: {csv_path}")

    def _generate_markdown_docs(self, dictionaries: dict[str, Any]):
        """生成 Markdown 文档"""
        md_content = self._generate_field_index_md(dictionaries)
        md_path = os.path.join(self.output_dir, "field_index.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"✓ 字段索引文档已保存到: {md_path}")

        for module, info in dictionaries["modules"].items():
            if not info.get("success"):
                continue
            module_md = self._generate_module_md(module, info)
            module_md_path = os.path.join(self.output_dir, f"{module}_dictionary.md")
            with open(module_md_path, "w", encoding="utf-8") as f:
                f.write(module_md)

    def _generate_field_index_md(self, dictionaries: dict[str, Any]) -> str:
        """生成字段索引 Markdown"""
        lines = [
            "# 字段索引",
            "",
            "本文档列出所有模块中使用的字段及其出现频率。",
            "",
            "## 概览",
            "",
            f"- 总模块数: {len(dictionaries['modules'])}",
            f"- 总字段数: {len(dictionaries['field_index'])}",
            "",
            "## 高频字段 (>5个模块)",
            "",
            "| 字段名 | 使用模块数 | 类型 | 示例值 |",
            "|--------|-----------|------|--------|",
        ]

        sorted_fields = sorted(
            dictionaries["field_index"].items(),
            key=lambda x: len(x[1]["modules"]),
            reverse=True,
        )

        for field, info in sorted_fields:
            if len(info["modules"]) > 5:
                samples = ", ".join(str(v) for v in info["sample_values"][:3])
                lines.append(
                    f"| {field} | {len(info['modules'])} | {', '.join(info['types'])} | {samples} |"
                )

        lines.extend(
            [
                "",
                "## 所有字段",
                "",
                "| 字段名 | 使用模块 |",
                "|--------|----------|",
            ]
        )

        for field, info in sorted_fields:
            modules_str = ", ".join(info["modules"][:5])
            if len(info["modules"]) > 5:
                modules_str += f" (+{len(info['modules']) - 5})"
            lines.append(f"| {field} | {modules_str} |")

        return "\n".join(lines)

    def _generate_module_md(self, module: str, info: dict[str, Any]) -> str:
        """生成单个模块的 Markdown 文档"""
        lines = [
            f"# {module} 模块数据字典",
            "",
            "## 概览",
            "",
            f"- 数据源: {info.get('sources', ['unknown'])}",
            f"- 字段数: {len(info.get('fields', {}))}",
            "",
            "## 字段列表",
            "",
            "| 字段名 | 数据类型 | 推断类型 | 金额单位 | 空值率 | 示例值 |",
            "|--------|---------|---------|---------|-------|--------|",
        ]

        for field, field_info in info.get("fields", {}).items():
            samples = ", ".join(str(v) for v in field_info.get("sample_values", [])[:2])
            lines.append(
                f"| {field} | {field_info.get('dtype', '')} | "
                f"{field_info.get('inferred_type', '')} | "
                f"{field_info.get('amount_unit', '-')} | "
                f"{field_info.get('null_rate', 0)}% | {samples} |"
            )

        if info.get("methods"):
            lines.extend(
                [
                    "",
                    "## 方法列表",
                    "",
                    "| 方法名 | 签名 |",
                    "|--------|------|",
                ]
            )
            for method in info["methods"]:
                lines.append(f"| {method['name']} | `{method['signature'] or ''}` |")

        return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="数据字典生成工具")
    parser.add_argument("--generate-all", action="store_true", help="生成所有模块的数据字典")
    parser.add_argument("--modules", help="指定模块（逗号分隔）")
    parser.add_argument("--output-dir", default="docs", help="输出目录")

    args = parser.parse_args()

    generator = DataDictionaryGenerator(output_dir=args.output_dir)

    if args.generate_all or args.modules:
        modules = None
        if args.modules:
            modules = [m.strip() for m in args.modules.split(",")]

        generator.generate_all_dictionaries(modules=modules)
    else:
        print("=" * 80)
        print("数据字典生成工具")
        print("=" * 80)
        print("\n使用方式:")
        print("  生成所有: python data_dictionary_generator.py --generate-all")
        print("  指定模块: python data_dictionary_generator.py --modules fundflow,northbound")
        print(f"\n可用模块: {generator.get_available_providers()}")


if __name__ == "__main__":
    from akshare_one.modules.field_naming import FieldType

    main()
