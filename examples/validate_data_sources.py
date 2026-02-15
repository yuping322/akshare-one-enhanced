#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接口验证脚本

本脚本用于验证 akshare-one-enhanced 项目的所有 37 个接口是否可用。

功能：
- 验证所有 12 个模块的 37 个接口
- 使用最简单的参数进行测试
- 打印验证结果和摘要报告

运行方式：
    python validate_data_sources.py

依赖：
- pandas
"""

import pandas as pd
import importlib
from datetime import datetime

# 导入异常类
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
)


class InterfaceValidator:
    """接口验证器"""

    def __init__(self):
        """初始化验证器"""
        self.results = []

    def validate_interface(self, module_name, interface_name, interface_func, test_params):
        """
        验证单个接口

        参数：
            module_name: 模块名称
            interface_name: 接口名称
            interface_func: 接口函数
            test_params: 测试参数字典

        返回：
            验证结果字典
        """
        result = {
            'module': module_name,
            'interface': interface_name,
            'status': 'unknown',
            'error_message': None,
            'row_count': None,
            'timestamp': datetime.now().isoformat()
        }

        try:
            # 调用接口
            df = interface_func(**test_params)

            # 验证数据结构
            if not isinstance(df, pd.DataFrame):
                raise ValueError("返回值不是 DataFrame")

            if df.empty:
                result['status'] = 'no_data'
                result['error_message'] = "返回数据为空"
            else:
                result['status'] = 'available'
                result['row_count'] = len(df)

        except NoDataError as e:
            result['status'] = 'no_data'
            result['error_message'] = f"无数据: {str(e)}"
        except DataSourceUnavailableError as e:
            result['status'] = 'unavailable'
            result['error_message'] = f"数据源不可用: {str(e)}"
        except InvalidParameterError as e:
            result['status'] = 'error'
            result['error_message'] = f"参数错误: {str(e)}"
        except Exception as e:
            result['status'] = 'error'
            result['error_message'] = f"错误: {str(e)}"

        self.results.append(result)
        return result

    def print_summary(self):
        """打印验证摘要"""
        total = len(self.results)
        available = sum(1 for r in self.results if r['status'] == 'available')
        no_data = sum(1 for r in self.results if r['status'] == 'no_data')
        unavailable = sum(1 for r in self.results if r['status'] == 'unavailable')
        error = sum(1 for r in self.results if r['status'] == 'error')

        print(f"\n{'='*80}")
        print("验证摘要")
        print(f"{'='*80}")
        print(f"总接口数: {total}")
        print(f"可用: {available} ({available/total*100:.1f}%)")
        print(f"无数据: {no_data} ({no_data/total*100:.1f}%)")
        print(f"不可用: {unavailable} ({unavailable/total*100:.1f}%)")
        print(f"错误: {error} ({error/total*100:.1f}%)")
        print(f"{'='*80}\n")


# 验证配置：为所有 37 个接口定义最简单的测试参数
VALIDATION_CONFIG = {
    # 1. FundFlow（资金流）- 7 个接口
    'fundflow': {
        'get_stock_fund_flow': {
            'symbol': '600000',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        },
        'get_sector_fund_flow': {
            'sector_type': 'industry',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        },
        'get_main_fund_flow_rank': {
            'date': '2024-01-15'
        },
        'get_industry_list': {},
        'get_industry_constituents': {
            'industry_code': 'BK0001'
        },
        'get_concept_list': {},
        'get_concept_constituents': {
            'concept_code': 'BK0001'
        }
    },

    # 2. Disclosure（公告信披）- 4 个接口
    'disclosure': {
        'get_disclosure_news': {
            'symbol': '600000',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'category': 'all'
        },
        'get_dividend_data': {
            'symbol': '600000',
            'start_date': '2020-01-01',
            'end_date': '2024-01-31'
        },
        'get_repurchase_data': {
            'symbol': None,
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        },
        'get_st_delist_data': {
            'symbol': None
        }
    },

    # 3. Northbound（北向资金）- 3 个接口
    'northbound': {
        'get_northbound_flow': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'market': 'sh'
        },
        'get_northbound_holdings': {
            'symbol': '600000',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        },
        'get_northbound_top_stocks': {
            'date': '2024-01-15',
            'market': 'sh',
            'top_n': 10
        }
    },

    # 4. Macro（宏观数据）- 6 个接口
    'macro': {
        'get_lpr_rate': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        },
        'get_pmi_index': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'pmi_type': 'manufacturing'
        },
        'get_cpi_data': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        },
        'get_ppi_data': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        },
        'get_m2_supply': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        },
        'get_shibor_rate': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
    },

    # 5. BlockDeal（大宗交易）- 2 个接口
    'blockdeal': {
        'get_block_deal': {
            'symbol': '600000',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        },
        'get_block_deal_summary': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'group_by': 'date'
        }
    },

    # 6. DragonTigerLHB（龙虎榜）- 3 个接口
    'lhb': {
        'get_dragon_tiger_list': {
            'date': '2024-01-15',
            'symbol': None
        },
        'get_dragon_tiger_summary': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'group_by': 'date'
        },
        'get_dragon_tiger_broker_stats': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'top_n': 10
        }
    },

    # 7. LimitUpDown（涨停池）- 3 个接口
    'limitup': {
        'get_limit_up_pool': {
            'date': '2024-01-15'
        },
        'get_limit_down_pool': {
            'date': '2024-01-15'
        },
        'get_limit_up_stats': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
    },

    # 8. MarginFinancing（融资融券）- 2 个接口
    'margin': {
        'get_margin_data': {
            'symbol': '600000',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        },
        'get_margin_summary': {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'market': 'sh'
        }
    },

    # 9. EquityPledge（股权质押）- 2 个接口
    'pledge': {
        'get_equity_pledge': {
            'symbol': '600000',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        },
        'get_equity_pledge_ratio_rank': {
            'date': '2024-01-15',
            'top_n': 10
        }
    },

    # 10. RestrictedRelease（限售解禁）- 2 个接口
    'restricted': {
        'get_restricted_release': {
            'symbol': '600000',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        },
        'get_restricted_release_calendar': {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
    },

    # 11. Goodwill（商誉）- 3 个接口
    'goodwill': {
        'get_goodwill_data': {
            'symbol': '600000',
            'start_date': '2020-01-01',
            'end_date': '2024-01-31'
        },
        'get_goodwill_impairment': {
            'date': '2024-01-15'
        },
        'get_goodwill_by_industry': {
            'date': '2024-01-15'
        }
    },

    # 12. ESG（ESG 评级）- 2 个接口
    'esg': {
        'get_esg_rating': {
            'symbol': '600000',
            'start_date': '2020-01-01',
            'end_date': '2024-01-31'
        },
        'get_esg_rating_rank': {
            'date': '2024-01-15',
            'industry': None,
            'top_n': 10
        }
    }
}


def main():
    """验证主函数"""
    print("=" * 80)
    print("接口验证脚本")
    print("=" * 80)
    print(f"\n开始验证时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("总模块数：12")
    print("总接口数：37\n")

    # 创建验证器
    validator = InterfaceValidator()

    # 遍历所有模块和接口进行验证
    for module_name, interfaces in VALIDATION_CONFIG.items():
        print(f"\n{'='*80}")
        print(f"验证模块: {module_name}")
        print(f"{'='*80}")

        # 动态导入模块
        try:
            if module_name == 'fundflow':
                module = importlib.import_module(f"akshare_one.{module_name}")
            else:
                module = importlib.import_module(f"akshare_one.modules.{module_name}")
        except ImportError as e:
            print(f"无法导入模块 {module_name}: {e}")
            continue

        # 验证每个接口
        for interface_name, params in interfaces.items():
            print(f"\n验证接口: {interface_name}")
            print(f"参数: {params}")

            try:
                # 获取接口函数
                interface_func = getattr(module, interface_name)

                # 验证接口
                result = validator.validate_interface(
                    module_name,
                    interface_name,
                    interface_func,
                    params
                )

                # 打印结果
                status_icon = "✓" if result['status'] == 'available' else "✗"
                status_text = result['status']

                if result['status'] == 'available':
                    print(f"{status_icon} 状态: {status_text} (返回 {result['row_count']} 行数据)")
                else:
                    print(f"{status_icon} 状态: {status_text}")
                    if result['error_message']:
                        print(f"  错误信息: {result['error_message']}")

            except AttributeError as e:
                print(f"✗ 接口不存在: {e}")
                validator.results.append({
                    'module': module_name,
                    'interface': interface_name,
                    'status': 'error',
                    'error_message': f"接口不存在: {e}",
                    'row_count': None,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"✗ 验证失败: {e}")
                validator.results.append({
                    'module': module_name,
                    'interface': interface_name,
                    'status': 'error',
                    'error_message': f"验证失败: {e}",
                    'row_count': None,
                    'timestamp': datetime.now().isoformat()
                })

    # 打印验证摘要
    validator.print_summary()

    # 打印详细结果表
    print("详细结果：")
    print(f"{'='*80}")
    print(f"{'模块':<15} {'接口':<35} {'状态':<15}")
    print(f"{'='*80}")

    for result in validator.results:
        status_icon = "✓" if result['status'] == 'available' else "✗"
        module = result['module']
        interface = result['interface']
        status = result['status']

        print(f"{status_icon} {module:<14} {interface:<34} {status:<15}")

        if result['error_message'] and result['status'] != 'available':
            # 截断错误信息以适应显示
            error_msg = result['error_message']
            if len(error_msg) > 60:
                error_msg = error_msg[:57] + "..."
            print(f"   错误: {error_msg}")

    print(f"{'='*80}\n")
    print(f"验证完成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    main()
