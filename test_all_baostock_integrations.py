#!/usr/bin/env python
"""
测试所有 Baostock 集成
"""
import sys
sys.path.insert(0, "src")

def test_imports():
    """测试所有模块导入"""
    print("=" * 60)
    print("测试 Baostock 模块导入")
    print("=" * 60)
    
    modules = [
        ("historical", "HistoricalDataFactory"),
        ("market", "InstrumentFactory"),
        ("financial", "FinancialDataFactory"),
        ("dividend", "DividendDataFactory"),
        ("performance", "PerformanceFactory"),
        ("macro", "MacroFactory"),
    ]
    
    for module_name, factory_name in modules:
        try:
            module = __import__(f"akshare_one.modules.{module_name}", fromlist=[factory_name])
            factory = getattr(module, factory_name)
            sources = factory.list_sources()
            has_baostock = "baostock" in sources
            
            status = "✅" if has_baostock else "❌"
            print(f"{status} {module_name:15} - {factory_name:25} - sources: {sources}")
            
            if not has_baostock:
                print(f"   ⚠️  baostock not registered in {module_name}")
        except Exception as e:
            print(f"❌ {module_name:15} - ERROR: {e}")
    
    print()

def test_providers():
    """测试 Provider 创建"""
    print("=" * 60)
    print("测试 Baostock Provider 创建")
    print("=" * 60)
    
    from akshare_one.modules.historical import HistoricalDataFactory
    from akshare_one.modules.market import InstrumentFactory
    from akshare_one.modules.financial import FinancialDataFactory
    from akshare_one.modules.dividend import DividendDataFactory
    from akshare_one.modules.performance import PerformanceFactory
    from akshare_one.modules.macro import MacroFactory
    
    tests = [
        ("HistoricalDataFactory", HistoricalDataFactory, "baostock", {"symbol": "600000", "interval": "day"}),
        ("InstrumentFactory", InstrumentFactory, "baostock", {}),
        ("FinancialDataFactory", FinancialDataFactory, "baostock", {"symbol": "600000"}),
        ("DividendDataFactory", DividendDataFactory, "baostock", {"symbol": "600000"}),
        ("PerformanceFactory", PerformanceFactory, "baostock", {"symbol": "600000"}),
        ("MacroFactory", MacroFactory, "baostock", {}),
    ]
    
    for name, factory, source, kwargs in tests:
        try:
            provider = factory.get_provider(source, **kwargs)
            print(f"✅ {name:25} - Provider created successfully")
        except Exception as e:
            print(f"❌ {name:25} - ERROR: {e}")
    
    print()

def test_methods():
    """测试方法存在性"""
    print("=" * 60)
    print("测试 Baostock 方法")
    print("=" * 60)
    
    from akshare_one.modules.historical import HistoricalDataFactory
    from akshare_one.modules.market import InstrumentFactory
    from akshare_one.modules.financial import FinancialDataFactory
    from akshare_one.modules.dividend import DividendDataFactory
    from akshare_one.modules.performance import PerformanceFactory
    from akshare_one.modules.macro import MacroFactory
    
    methods_map = {
        "Historical": ["get_hist_data", "get_trade_dates"],
        "Instrument": ["query_all_stock", "query_stock_basic", "query_stock_industry", 
                       "query_hs300_stocks", "query_sz50_stocks", "query_zz500_stocks"],
        "Financial": ["get_profit_data", "get_operation_data", "get_growth_data",
                      "get_balance_data", "get_cash_flow_data", "get_dupont_data"],
        "Dividend": ["get_dividend_data", "get_adjust_factor"],
        "Performance": ["get_forecast_report", "get_performance_express_report"],
        "Macro": ["get_deposit_rate_data", "get_loan_rate_data", 
                  "get_required_reserve_ratio_data", "get_money_supply_data_month",
                  "get_money_supply_data_year"],
    }
    
    factories_map = {
        "Historical": HistoricalDataFactory,
        "Instrument": InstrumentFactory,
        "Financial": FinancialDataFactory,
        "Dividend": DividendDataFactory,
        "Performance": PerformanceFactory,
        "Macro": MacroFactory,
    }
    
    for module, methods in methods_map.items():
        factory = factories_map[module]
        try:
            provider = factory.get_provider("baostock", symbol="600000" if module != "Macro" else None)
            missing = []
            for method in methods:
                if not hasattr(provider, method):
                    missing.append(method)
            
            if missing:
                print(f"⚠️  {module:15} - Missing methods: {missing}")
            else:
                print(f"✅ {module:15} - All {len(methods)} methods present")
        except Exception as e:
            print(f"❌ {module:15} - ERROR: {e}")
    
    print()

def main():
    print("\n" + "=" * 60)
    print("Baostock 集成完整性测试")
    print("=" * 60 + "\n")
    
    test_imports()
    test_providers()
    test_methods()
    
    print("=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
