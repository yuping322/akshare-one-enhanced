#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接口检查脚本

本脚本用于遍历所有 37 个接口并检查可用性。
使用固定参数进行快速检查，参考示例程序中的参数模式。

功能：
- 遍历所有 12 个模块的 37 个接口
- 使用固定参数进行检查
- 打印每个接口的状态
- 生成摘要报告

运行方式：
    python scripts/monitor_data_sources.py

依赖：
- pandas
"""

import sys
from datetime import datetime
import pandas as pd
import importlib

# 导入异常类
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
    UpstreamChangedError,
)


class InterfaceChecker:
    """接口检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.results = []
    
    def check_all_interfaces(self):
        """检查所有接口"""
        print("开始检查所有接口...")
        print(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 遍历所有模块和接口
        for module_name, interfaces in INTERFACE_CONFIG.items():
            print(f"\n{'='*80}")
            print(f"检查模块: {module_name}")
            print(f"{'='*80}")
            
            # 动态导入模块
            try:
                module = importlib.import_module(f"akshare_one.modules.{module_name}")
            except ImportError as e:
                print(f"✗ 无法导入模块: {e}")
                for interface_name in interfaces.keys():
                    self.results.append({
                        'module': module_name,
                        'interface': interface_name,
                        'status': 'error',
                        'error': f"模块导入失败: {e}"
                    })
                continue
            
            # 检查每个接口
            for interface_name, params in interfaces.items():
                print(f"  检查接口: {interface_name}...", end=" ")
                
                try:
                    # 获取接口函数
                    interface_func = getattr(module, interface_name)
                    
                    # 调用接口
                    df = interface_func(**params)
                    
                    # 验证结果
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        print(f"✓ 可用 (返回 {len(df)} 行)")
                        self.results.append({
                            'module': module_name,
                            'interface': interface_name,
                            'status': 'available',
                            'row_count': len(df)
                        })
                    elif isinstance(df, pd.DataFrame) and df.empty:
                        print("✗ 无数据")
                        self.results.append({
                            'module': module_name,
                            'interface': interface_name,
                            'status': 'no_data'
                        })
                    else:
                        print("✗ 返回值类型错误")
                        self.results.append({
                            'module': module_name,
                            'interface': interface_name,
                            'status': 'error',
                            'error': '返回值不是 DataFrame'
                        })
                
                except NoDataError as e:
                    print(f"✗ 无数据: {str(e)[:50]}")
                    self.results.append({
                        'module': module_name,
                        'interface': interface_name,
                        'status': 'no_data',
                        'error': str(e)
                    })
                except DataSourceUnavailableError as e:
                    print(f"✗ 数据源不可用: {str(e)[:50]}")
                    self.results.append({
                        'module': module_name,
                        'interface': interface_name,
                        'status': 'unavailable',
                        'error': str(e)
                    })
                except AttributeError as e:
                    print(f"✗ 接口不存在: {str(e)[:50]}")
                    self.results.append({
                        'module': module_name,
                        'interface': interface_name,
                        'status': 'error',
                        'error': f"接口不存在: {e}"
                    })
                except Exception as e:
                    print(f"✗ 失败: {str(e)[:50]}")
                    self.results.append({
                        'module': module_name,
                        'interface': interface_name,
                        'status': 'error',
                        'error': str(e)
                    })
        
        # 打印摘要
        self.print_summary()
    
    def print_summary(self):
        """打印检查摘要"""
        total = len(self.results)
        available = sum(1 for r in self.results if r['status'] == 'available')
        no_data = sum(1 for r in self.results if r['status'] == 'no_data')
        unavailable = sum(1 for r in self.results if r['status'] == 'unavailable')
        error = sum(1 for r in self.results if r['status'] == 'error')
        
        print(f"\n{'='*80}")
        print(f"检查完成")
        print(f"{'='*80}")
        print(f"总接口数: {total}")
        print(f"可用: {available} ({available/total*100:.1f}%)")
        print(f"无数据: {no_data} ({no_data/total*100:.1f}%)")
        print(f"不可用: {unavailable} ({unavailable/total*100:.1f}%)")
        print(f"错误: {error} ({error/total*100:.1f}%)")
        print(f"{'='*80}")


# 固定参数配置
# 参考示例程序中的参数使用方式
FIXED_PARAMS = {
    'symbol': '600000',           # 浦发银行
    'date': '2024-01-15',         # 固定日期
    'start_date': '2024-01-01',   # 固定开始日期
    'end_date': '2024-01-31',     # 固定结束日期
    'sector_type': 'industry',    # 行业类型
    'market': 'sh',               # 上海市场
    'industry_code': 'BK0001',    # 行业代码
    'concept_code': 'BK0001',     # 概念代码
    'pmi_type': 'manufacturing',  # PMI 类型
    'top_n': 10,                  # 排名数量
    'indicator': 'net_inflow',    # 指标类型
    'category': 'all',            # 分类
    'group_by': 'date'            # 分组方式
}


# 接口配置：所有 37 个接口及其固定参数
INTERFACE_CONFIG = {
    # 1. FundFlow（资金流）- 7 个接口
    'fundflow': {
        'get_stock_fund_flow': {
            'symbol': FIXED_PARAMS['symbol'],
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_sector_fund_flow': {
            'sector_type': FIXED_PARAMS['sector_type'],
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_main_fund_flow_rank': {
            'date': FIXED_PARAMS['date']
        },
        'get_industry_list': {},
        'get_industry_constituents': {
            'industry_code': FIXED_PARAMS['industry_code']
        },
        'get_concept_list': {},
        'get_concept_constituents': {
            'concept_code': FIXED_PARAMS['concept_code']
        }
    },
    
    # 2. Disclosure（公告信披）- 4 个接口
    'disclosure': {
        'get_disclosure_news': {
            'symbol': FIXED_PARAMS['symbol'],
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date'],
            'category': FIXED_PARAMS['category']
        },
        'get_dividend_data': {
            'symbol': FIXED_PARAMS['symbol'],
            'start_date': '2020-01-01',
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_repurchase_data': {
            'symbol': None,
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_st_delist_data': {
            'symbol': None
        }
    },
    
    # 3. Northbound（北向资金）- 3 个接口
    'northbound': {
        'get_northbound_flow': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date'],
            'market': FIXED_PARAMS['market']
        },
        'get_northbound_holdings': {
            'symbol': FIXED_PARAMS['symbol'],
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_northbound_top_stocks': {
            'date': FIXED_PARAMS['date'],
            'market': FIXED_PARAMS['market'],
            'top_n': FIXED_PARAMS['top_n']
        }
    },
    
    # 4. Macro（宏观数据）- 6 个接口
    'macro': {
        'get_lpr_rate': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_pmi_index': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date'],
            'pmi_type': FIXED_PARAMS['pmi_type']
        },
        'get_cpi_data': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_ppi_data': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_m2_supply': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_shibor_rate': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        }
    },
    
    # 5. BlockDeal（大宗交易）- 2 个接口
    'blockdeal': {
        'get_block_deal': {
            'symbol': FIXED_PARAMS['symbol'],
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_block_deal_summary': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date'],
            'group_by': FIXED_PARAMS['group_by']
        }
    },
    
    # 6. DragonTigerLHB（龙虎榜）- 3 个接口
    'lhb': {
        'get_dragon_tiger_list': {
            'date': FIXED_PARAMS['date'],
            'symbol': None
        },
        'get_dragon_tiger_summary': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date'],
            'group_by': FIXED_PARAMS['group_by']
        },
        'get_dragon_tiger_broker_stats': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date'],
            'top_n': FIXED_PARAMS['top_n']
        }
    },
    
    # 7. LimitUpDown（涨停池）- 3 个接口
    'limitup': {
        'get_limit_up_pool': {
            'date': FIXED_PARAMS['date']
        },
        'get_limit_down_pool': {
            'date': FIXED_PARAMS['date']
        },
        'get_limit_up_stats': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        }
    },
    
    # 8. MarginFinancing（融资融券）- 2 个接口
    'margin': {
        'get_margin_data': {
            'symbol': FIXED_PARAMS['symbol'],
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_margin_summary': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date'],
            'market': FIXED_PARAMS['market']
        }
    },
    
    # 9. EquityPledge（股权质押）- 2 个接口
    'pledge': {
        'get_equity_pledge': {
            'symbol': FIXED_PARAMS['symbol'],
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_equity_pledge_ratio_rank': {
            'date': FIXED_PARAMS['date'],
            'top_n': FIXED_PARAMS['top_n']
        }
    },
    
    # 10. RestrictedRelease（限售解禁）- 2 个接口
    'restricted': {
        'get_restricted_release': {
            'symbol': FIXED_PARAMS['symbol'],
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': '2024-12-31'
        },
        'get_restricted_release_calendar': {
            'start_date': FIXED_PARAMS['start_date'],
            'end_date': '2024-12-31'
        }
    },
    
    # 11. Goodwill（商誉）- 3 个接口
    'goodwill': {
        'get_goodwill_data': {
            'symbol': FIXED_PARAMS['symbol'],
            'start_date': '2020-01-01',
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_goodwill_impairment': {
            'date': FIXED_PARAMS['date']
        },
        'get_goodwill_by_industry': {
            'date': FIXED_PARAMS['date']
        }
    },
    
    # 12. ESG（ESG 评级）- 2 个接口
    'esg': {
        'get_esg_rating': {
            'symbol': FIXED_PARAMS['symbol'],
            'start_date': '2020-01-01',
            'end_date': FIXED_PARAMS['end_date']
        },
        'get_esg_rating_rank': {
            'date': FIXED_PARAMS['date'],
            'industry': None,
            'top_n': FIXED_PARAMS['top_n']
        }
    }
}


def main():
    """检查主函数"""
    print("=" * 80)
    print("接口检查脚本")
    print("=" * 80)
    print(f"\n本脚本将遍历所有 37 个接口并检查可用性")
    print(f"使用固定参数进行快速检查\n")
    
    # 创建检查器
    checker = InterfaceChecker()
    
    # 检查所有接口
    checker.check_all_interfaces()
    
    print(f"\n检查完成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    main()
