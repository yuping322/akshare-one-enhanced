"""
单位转换器模块

处理金额字段的单位转换，支持元、万元、亿元之间的转换。
"""

import pandas as pd


class UnitConverter:
    """单位转换器"""
    
    # 单位转换系数（相对于元）
    UNIT_MULTIPLIERS = {
        'yuan': 1,           # 元
        'wan_yuan': 10000,   # 万元
        'yi_yuan': 100000000 # 亿元
    }
    
    def convert_amount(
        self, 
        value: float, 
        from_unit: str, 
        to_unit: str = 'yuan'
    ) -> float:
        """
        转换金额单位
        
        Args:
            value: 原始值
            from_unit: 源单位（'yuan', 'wan_yuan', 'yi_yuan'）
            to_unit: 目标单位（默认为 'yuan'）
        
        Returns:
            转换后的值
        
        Raises:
            ValueError: 如果单位不支持
        """
        if from_unit not in self.UNIT_MULTIPLIERS:
            raise ValueError(
                f"Unsupported source unit '{from_unit}'. "
                f"Supported units: {list(self.UNIT_MULTIPLIERS.keys())}"
            )
        
        if to_unit not in self.UNIT_MULTIPLIERS:
            raise ValueError(
                f"Unsupported target unit '{to_unit}'. "
                f"Supported units: {list(self.UNIT_MULTIPLIERS.keys())}"
            )
        
        # 先转换为元，再转换为目标单位
        value_in_yuan = value * self.UNIT_MULTIPLIERS[from_unit]
        result = value_in_yuan / self.UNIT_MULTIPLIERS[to_unit]
        
        return result
    
    def convert_dataframe_amounts(
        self, 
        df: pd.DataFrame, 
        amount_fields: dict[str, str]
    ) -> pd.DataFrame:
        """
        转换DataFrame中所有金额字段的单位
        
        Args:
            df: 原始DataFrame
            amount_fields: 字段名到源单位的映射，例如 {'balance': 'yi_yuan', 'amount': 'wan_yuan'}
        
        Returns:
            单位已转换的DataFrame（所有金额字段转换为元）
        """
        df_copy = df.copy()
        
        for field_name, source_unit in amount_fields.items():
            if field_name in df_copy.columns:
                # 转换该字段的所有值
                df_copy[field_name] = df_copy[field_name].apply(
                    lambda x: self.convert_amount(x, source_unit, 'yuan') 
                    if pd.notna(x) else x
                )
        
        return df_copy
    
    def detect_unit(self, values: pd.Series) -> str:
        """
        自动检测金额字段的单位（基于数值范围的启发式方法）
        
        Args:
            values: 金额值序列
        
        Returns:
            检测到的单位（'yuan', 'wan_yuan', 'yi_yuan'）
        
        Note:
            这是一个启发式方法，基于以下假设：
            - 如果平均值 < 100,000，可能是万元
            - 如果平均值 < 1,000，可能是亿元
            - 否则可能是元
            
            此方法不保证准确，建议在配置中明确指定单位
        """
        # 过滤掉 NaN 和非正值
        valid_values = values[pd.notna(values) & (values > 0)]
        
        if len(valid_values) == 0:
            return 'yuan'  # 默认返回元
        
        # 计算中位数（比平均值更稳健）
        median_value = valid_values.median()
        
        # 启发式判断
        if median_value < 1000:
            return 'yi_yuan'  # 可能是亿元
        elif median_value < 100000:
            return 'wan_yuan'  # 可能是万元
        else:
            return 'yuan'  # 可能是元
