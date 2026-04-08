"""
字段命名标准化系统的核心数据模型

包含字段类型枚举、命名规则、字段映射和映射配置等数据类。
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FieldType(Enum):
    """字段类型枚举"""

    # 日期/时间类型
    DATE = "date"  # 日期字段
    TIMESTAMP = "timestamp"  # 时间戳字段
    EVENT_DATE = "event_date"  # 事件日期
    TIME = "time"  # 时间字段
    DURATION = "duration"  # 持续时间

    # 金额类型
    AMOUNT = "amount"  # 金额
    BALANCE = "balance"  # 余额
    VALUE = "value"  # 市值
    NET_FLOW = "net_flow"  # 净流量

    # 比率类型
    RATE = "rate"  # 变化率
    RATIO = "ratio"  # 结构比例

    # 标识符类型
    SYMBOL = "symbol"  # 股票代码
    NAME = "name"  # 名称
    CODE = "code"  # 代码
    MARKET = "market"  # 市场
    RANK = "rank"  # 排名
    ANALYST = "analyst"  # 分析师
    INSTITUTION = "institution"  # 机构

    # 数量类型
    COUNT = "count"  # 计数
    VOLUME = "volume"  # 成交量
    SHARES = "shares"  # 股份

    # 特殊类型
    BOOLEAN = "boolean"  # 布尔标志
    TYPE = "type"  # 类型/类别
    OTHER = "other"  # 其他


@dataclass
class NamingRules:
    """字段命名规则配置"""

    # 日期/时间字段规则
    date_field_pattern: str = r"^date$"
    event_date_field_pattern: str = r"^[a-z_]+_date$"
    timestamp_field_name: str = "timestamp"
    time_field_pattern: str = r"^[a-z_]+_time$"
    duration_field_pattern: str = r"^[a-z_]+_(days|duration)$"

    # 金额字段规则
    amount_field_pattern: str = r"^([a-z_]+_amount|amount|price|close|open|high|low|last|bid|ask|equity|value|revenue|net_profit|total_assets|total_liabilities|eps)$"
    balance_field_pattern: str = r"^([a-z_]+_balance|balance)$"
    value_field_pattern: str = r"^([a-z_]+_value|value)$"
    net_flow_pattern: str = r"^([a-z_]+_net_(inflow|outflow|buy|sell)|net_flow)$"

    # 比率字段规则
    rate_field_pattern: str = r"^([a-z_]+_rate|rate|pct_change|turnover_rate)$"
    ratio_field_pattern: str = r"^([a-z_]+_ratio|ratio)$"

    # 标识符字段规则
    symbol_field_name: str = "symbol"
    name_field_name: str = "name"
    code_field_pattern: str = r"^[a-z_]+_code$"
    market_field_name: str = "market"
    rank_field_name: str = "rank"
    analyst_field_name: str = "analyst"
    institution_field_name: str = "institution"

    # 计数字段规则
    count_field_pattern: str = r"^[a-z_]+_count$"

    # 股份/成交量字段规则
    volume_field_name: str = "volume"
    shares_field_pattern: str = r"^[a-z_]+_shares$"

    # 特殊字段规则
    boolean_field_pattern: str = r"^(is|has)_[a-z_]+$"
    type_field_pattern: str = r"^[a-z_]+_(type|category)$"

    def _get_pattern_for_type(self, field_type: FieldType) -> str:
        """获取字段类型对应的命名模式"""
        pattern_map = {
            FieldType.DATE: self.date_field_pattern,
            FieldType.EVENT_DATE: self.event_date_field_pattern,
            FieldType.TIMESTAMP: f"^{self.timestamp_field_name}$",
            FieldType.TIME: self.time_field_pattern,
            FieldType.DURATION: self.duration_field_pattern,
            FieldType.AMOUNT: self.amount_field_pattern,
            FieldType.BALANCE: self.balance_field_pattern,
            FieldType.VALUE: self.value_field_pattern,
            FieldType.NET_FLOW: self.net_flow_pattern,
            FieldType.RATE: self.rate_field_pattern,
            FieldType.RATIO: self.ratio_field_pattern,
            FieldType.SYMBOL: f"^{self.symbol_field_name}$",
            FieldType.NAME: f"^{self.name_field_name}$",
            FieldType.CODE: self.code_field_pattern,
            FieldType.MARKET: f"^{self.market_field_name}$",
            FieldType.RANK: f"^{self.rank_field_name}$",
            FieldType.ANALYST: f"^{self.analyst_field_name}$",
            FieldType.INSTITUTION: f"^{self.institution_field_name}$",
            FieldType.COUNT: self.count_field_pattern,
            FieldType.VOLUME: f"^{self.volume_field_name}$",
            FieldType.SHARES: self.shares_field_pattern,
            FieldType.BOOLEAN: self.boolean_field_pattern,
            FieldType.TYPE: self.type_field_pattern,
            FieldType.OTHER: r".*",  # 其他类型接受任何模式
        }
        return pattern_map.get(field_type, r".*")

    def validate_field_name(self, field_name: str, field_type: FieldType) -> bool:
        """
        验证字段名是否符合规则

        Args:
            field_name: 待验证的字段名
            field_type: 字段类型

        Returns:
            是否符合规则
        """
        pattern = self._get_pattern_for_type(field_type)
        return bool(re.match(pattern, field_name))


@dataclass
class FieldMapping:
    """字段映射配置"""

    source_field: str  # 源字段名
    standard_field: str  # 标准字段名
    field_type: FieldType  # 字段类型
    source_unit: str | None = None  # 源单位（金额字段）
    target_unit: str = "yuan"  # 目标单位
    transform: Callable | None = None  # 自定义转换函数
    description: str = ""  # 映射说明

    def apply(self, value: Any) -> Any:
        """
        应用映射转换

        Args:
            value: 原始值

        Returns:
            转换后的值
        """
        if self.transform:
            return self.transform(value)
        return value


@dataclass
class MappingConfig:
    """模块级别的映射配置"""

    source: str  # 数据源名称
    module: str  # 模块名称
    mappings: list[FieldMapping] = field(default_factory=list)  # 字段映射列表
    version: str = "1.0"  # 配置版本
    last_updated: str = ""  # 最后更新时间

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            字典表示
        """
        return {
            "source": self.source,
            "module": self.module,
            "version": self.version,
            "last_updated": self.last_updated,
            "mappings": [
                {
                    "source_field": m.source_field,
                    "standard_field": m.standard_field,
                    "field_type": m.field_type.value,
                    "source_unit": m.source_unit,
                    "target_unit": m.target_unit,
                    "description": m.description,
                }
                for m in self.mappings
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MappingConfig":
        """
        从字典创建配置

        Args:
            data: 字典数据

        Returns:
            MappingConfig 实例
        """
        mappings = []
        for m in data.get("mappings", []):
            try:
                raw_type = m.get("field_type", "other")
                try:
                    field_type = FieldType(raw_type.lower())
                except ValueError:
                    field_type = FieldType.OTHER

                mappings.append(
                    FieldMapping(
                        source_field=m["source_field"],
                        standard_field=m["standard_field"],
                        field_type=field_type,
                        source_unit=m.get("source_unit"),
                        target_unit=m.get("target_unit", "yuan"),
                        description=m.get("description", ""),
                    )
                )
            except KeyError as e:
                # 记录日志或跳过缺失必填字段的映射
                continue

        return cls(
            source=data["source"],
            module=data["module"],
            mappings=mappings,
            version=data.get("version", "1.0"),
            last_updated=data.get("last_updated", ""),
        )


# 预定义字段等价关系（标准字段 -> 等价字段列表）
# 基于 quant_skills 项目的数据驱动分析结果扩展
FIELD_EQUIVALENTS = {
    # 日期相关
    "date": [
        "日期",
        "DATE",
        "TRADE_DATE",
        "交易日期",
        "更新日期",
        "公告日期",
        "上市日期",
        "成立日期",
        "报告期",
        "报告日",
        "变动日期",
        "净值日期",
        "统计时间",
        "发布时间",
        "更新时间",
        "停牌日期",
        "预计复牌日期",
        "申购日期",
        "更新日期",
        "公告日期",
        "日期",
        "start_date",
        "end_date",
        "trade_date",
        "REPORT_DATE",
        "START_DATE",
        "NOTICE_DATE",
        "FINANCIAL_DATE",
        "DATE_TYPE",
        "month",
        "月份",
        "DATE_TYPE_CODE",
        "STD_REPORT_DATE",
        "update_time",
        "year",
    ],
    # 报告日期 - 单独作为标准字段，不自动映射到date
    "report_date": [
        "report_date",
    ],
    # 代码相关
    "symbol": [
        "代码",
        "股票代码",
        "基金代码",
        "指数代码",
        "债券代码",
        "期货代码",
        "合约代码",
        "code",
        "stock_code",
        "fund_code",
        "证券代码",
        "stock",
        "公司代码",
        "bond_code",
        "bond_name",
        "bond_code",
        "SYMBOL",
        "CODE",
        "标的证券代码",
    ],
    "sector_code": ["板块代码", "板块ID", "行业代码", "概念代码", "sector_code", "board_code"],
    "sector_name": ["板块名称", "板块", "行业名称", "概念名称", "sector_name", "board_name", "名称"],
    # 名称相关
    "name": [
        "名称",
        "股票名称",
        "基金名称",
        "指数名称",
        "债券名称",
        "期货名称",
        "商品",
        "股票简称",
        "基金简称",
        "债券简称",
        "证券简称",
        "简称",
        "公司简称",
        "报告名称",
        "report_name",
        "quarter_name",
        "metric_name",
        "SECURITY_NAME_ABBR",
        "STD_ITEM_NAME",
        "ITEM_NAME",
        "REPORT_DATE_NAME",
        "营业部名称",
        "股东名称",
    ],
    # 标题相关
    "title": [
        "标题",
        "新闻标题",
        "title",
        "新闻名称",
    ],
    # 计数/数量相关
    "constituent_count": ["公司数量", "成分股数量", "股票数量", "constituent_count", "stock_count"],
    # 资金流向相关 - 使用fundflow模块特定字段名
    "main_net_inflow": ["net_inflow", "main_net_inflow"],
    "main_net_inflow_rate": ["net_inflow_rate", "main_net_inflow_rate"],
    "pct_change": ["今日涨跌幅", "涨跌幅", "pct_chg", "chg_pct", "percent", "涨跌幅(%)"],
    "leading_stock": ["今日主力净流入最大股", "领涨股", "leading_stock"],
    "analyst": ["分析师名称", "分析师", "analyst", "analyst_name"],
    "institution": ["分析师单位", "机构", "机构名称", "institution", "agency", "research_institute"],
    # 价格相关
    "close": [
        "收盘价",
        "CLOSE",
        "最新价",
        "现价",
        "收盘",
        "收盘",
        "_close",
        "latest_price",
        "last_price",
    ],
    "open": ["开盘价", "OPEN", "今开", "开盘", "_open"],
    "high": ["最高价", "HIGH", "最高", "_high"],
    "low": ["最低价", "LOW", "最低", "_low"],
    # 成交量相关
    "volume": ["成交量", "VOLUME", "成交量(手)", "成交手数", "volume", "交易量", "VOL", "turnover"],
    "amount": ["成交额", "AMOUNT", "成交额(万)", "成交金额", "amount", "turnover_value"],
    # 涨跌幅相关
    "change_pct": [
        "涨跌幅",
        "涨跌",
        "涨跌幅(%)",
        "change",
        "变动",
        "pct_change",
        "涨跌额",
        "CHANGE",
        "percent",
        "percent_change",
        "rate",
        "change_rate",
    ],
    "change_amount": ["涨跌额", "变化值", "change_amount", "涨跌金额"],
    # 评级与机构相关
    "rating": ["评级", "东财评级", "rating", "rating_name", "RESEARCH_RATING"],
    "industry": ["行业", "所属行业", "industry", "sector", "INDUSTRY"],
    "report_title": ["报告名称", "研报标题", "report_title", "RESEARCH_TITLE"],
    #  amplitudes
    "amplitude": ["振幅", "amplitude", "振幅(%)"],
    # 金融指标
    "net_flow": [
        "净流入",
        "主力净流入",
        "净买额",
        "净买入",
        "net_buy",
    ],
    "net_flow_rate": [
        "净流入率",
        "净买率",
        "净买入率",
        "rate",
    ],
    # 市值相关
    "market_cap": ["总市值", "市值", "market_cap", "total_market_cap", "market_value"],
    "float_market_cap": ["流通市值", "float_market_cap", "circulation_market_value"],
    # 估值指标
    "pe_ratio": ["市盈率", "市盈率-动态", "PE", "pe_ratio", "price_to_earnings_ratio"],
    "pb_ratio": ["市净率", "PB", "pb_ratio", "price_to_book_ratio"],
    # 换手率
    "turnover_rate": ["换手率", "换手率(%)", "turnover_rate", "turnover_ratio"],
    # 基金相关
    "net_value": ["单位净值", "净值", "net_value", "nav", "net_asset_value"],
    "daily_growth": ["日增长率", "日增长", "daily_growth", "daily_return"],
    "fund_manager": ["基金经理", "管理人名", "manager"],
    "fund_company": ["基金公司", "管理公司", "company", "fund_company"],
    # 其他常见字段
    "value": ["数值", "值", "mid_convert_value", "value", "val"],
    "industry": ["所属行业", "行业", "industry", "sector", "板块"],
    "volume_ratio": ["量比", "volume_ratio", "相对成交量"],
    "change_speed": ["涨速", "change_speed"],
    "location": ["注册地", "地区", "location", "area"],
    "total_shares": ["总股本", "total_shares", "total_share"],
    "issue_price": ["发行价格", "发行价", "issue_price", "offer_price"],
    "avg_price": ["均价", "average_price", "avg_price"],
    "holding_value": ["持股市值", "holding_value", "market_value_of_holding"],
    # 财务报表相关
    "revenue": ["营业收入", "营收", "revenue", "operating_revenue", "sales"],
    "profit": ["净利润", "利润", "profit", "net_profit", "earnings"],
    "assets": ["总资产", "资产总计", "assets"],
    "liabilities": ["总负债", "负债合计", "liabilities", "total_liabilities"],
    "equity": ["所有者权益", "股东权益", "equity", "shareholders_equity"],
    "current_assets": ["流动资产合计", "流动资产", "current_assets"],
    "non_current_assets": ["非流动资产合计", "非流动资产", "non_current_assets"],
    "cash_and_equivalents": ["货币资金", "现金及现金等价物", "现金及存放中央银行款项", "cash_and_equivalents"],
    "accounts_receivable": ["应收账款", "应收款项", "accounts_receivable", "trade_receivables"],
    "inventory": ["存货", "库存商品", "inventory"],
    "total_liabilities": ["负债合计", "负债总计", "total_liabilities"],
    "current_liabilities": ["流动负债合计", "流动负债", "current_liabilities"],
    "non_current_liabilities": ["非流动负债合计", "非流动负债", "non_current_liabilities"],
    "shareholders_equity": ["股东权益合计", "归属于母公司股东的权益", "股东权益", "shareholders_equity"],
    "fixed_assets_net": ["固定资产净值", "固定资产净额", "fixed_assets_net"],
    "construction_in_progress": ["在建工程", "construction_in_progress", "在建工程余额"],
    "goodwill": ["商誉", "goodwill"],
    "intangible_assets": ["无形资产", "intangible_assets"],
    "long_term_equity_investment": ["长期股权投资", "long_term_equity_investment"],
    "accounts_payable": ["应付账款", "应付款项", "accounts_payable", "trade_payables"],
    "advance_receivables": ["预收账款", "合同负债", "advance_receivables"],
    "deferred_revenue": ["递延收益", "deferred_revenue"],
    "current_debt": ["短期借款", "短期贷款", "current_debt"],
    "non_current_debt": ["长期借款", "长期贷款", "non_current_debt"],
    "capital_reserve": ["资本公积", "capital_reserve"],
    "minority_interest": ["少数股东权益", "minority_interest", "少数股权"],
    "net_income": ["净利润", "归属母公司净利润", "net_income"],
    "operating_profit": ["营业利润", "operating_profit"],
    "total_operating_costs": ["营业总成本", "总成本", "total_operating_costs"],
    "cost_of_revenue": ["营业成本", "cost_of_revenue"],
    "gross_profit": ["毛利润", "毛利", "gross_profit"],
    "selling_expenses": ["销售费用", "selling_expenses"],
    "administrative_expenses": ["管理费用", "administrative_expenses"],
    "financial_expenses": ["财务费用", "financial_expenses"],
    "research_development": ["研发费用", "研发投入", "research_development", "R&D"],
    "investment_income": ["投资收益", "investment_income"],
    "net_cash_flow_from_operations": ["经营活动产生的现金流量净额", "经营活动现金流", "net_cash_flow_from_operations"],
    "net_cash_flow_from_investing": ["投资活动产生的现金流量净额", "投资活动现金流", "net_cash_flow_from_investing"],
    "net_cash_flow_from_financing": ["筹资活动产生的现金流量净额", "筹资活动现金流", "net_cash_flow_from_financing"],
    "ending_cash_balance": ["期末现金及现金等价物余额", "期末现金余额", "ending_cash_balance"],
    "total_assets": ["资产总计", "total_assets"],
    "currency": ["币种", "货币", "currency"],
    # 龙虎榜相关
    "department": ["营业部", "买卖营业部", "department", "sales_department"],
    "buy_amount": ["买入金额", "净买入金额", "buy_amount", "purchase_amount", "买入成交额"],
    "sell_amount": ["卖出金额", "sell_amount", "sales_amount", "卖出成交额"],
    # 限价相关
    "limit_up": ["涨停价", "最高限价", "limit_up", "upper_limit"],
    "limit_down": ["跌停价", "最低限价", "limit_down", "lower_limit"],
    # 大宗交易相关
    "block_trade_price": ["成交价格", "大宗交易价格", "block_trade_price"],
    "block_trade_volume": ["成交数量", "大宗交易量", "block_trade_volume"],
    # 质押相关
    "pledge_shares": ["质押股数", "质押数量", "pledge_shares", "pledged_shares"],
    "pledge_ratio": ["质押比例", "质押率", "pledge_ratio", "pledge_rate"],
    "pledgee": ["质权人", "质押人", "pledgee", "pledgor"],
    "pledge_date": ["质押日期", "质押时间", "pledge_date", "pledged_date"],
    # 北上资金相关
    "net_buy": ["净买入", "净买额", "net_buy", "net_purchase", "净流入"],
    # 涨跌停相关
    "limit_up_price": ["涨停价", "upper_limit_price"],
    "limit_down_price": ["跌停价", "lower_limit_price"],
    # 公告相关
    "announcement_title": ["公告标题", "公告名称", "announcement_title", "title"],
    "announcement_type": ["公告类型", "announcement_type", "type"],
    # 报告期相关
    "report_period": ["报告期", "报告期间", "report_period", "period"],
    # 市场相关
    "market": ["市场", "交易所", "exchange", "market", "MARKET"],
    "adjust": ["复权", "复权类型", "adjust", "adjust_type"],
    # 周期相关
    "period": ["周期", "frequency", "period", "interval"],
    # 排名相关
    "rank": ["排名", "rank", "排序", "排行"],
    # 其他
    "type": ["类型", "品种", "type", "category"],
    "status": ["状态", "申购状态", "赎回状态", "status", "state"],
    "index": ["指数", "指数代码", "index", "index_code"],
    "issue_year": ["发行年份", "上市年份", "issue_year", "listing_year"],
    "fee": ["手续费", "费用", "fee", "commission", "费用"],
    "qvix": [],
}
