from .base import BatchQueryFactory
from ..base import BaseProvider


@BatchQueryFactory.register("local")
class LocalBatchQueryProvider(BaseProvider):
    """本地批量查询提供者（组合现有单只查询）"""

    def get_source_name(self) -> str:
        return "local"

    def get_data_type(self) -> str:
        return "batchquery"
