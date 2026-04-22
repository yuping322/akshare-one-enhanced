from .base import AnalysisFactory
from ..core.base import BaseProvider


@AnalysisFactory.register("local")
class LocalAnalysisProvider(BaseProvider):
    """本地分析函数提供者（不需要外部数据源）"""

    def get_source_name(self) -> str:
        return "local"

    def get_data_type(self) -> str:
        return "analysis"
