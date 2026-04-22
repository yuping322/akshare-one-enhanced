from ..base import BaseProvider
from ..factory_base import BaseFactory
import pandas as pd


class BatchQueryProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "batchquery"


class BatchQueryFactory(BaseFactory[BatchQueryProvider]):
    _providers: dict[str, type[BatchQueryProvider]] = {}
