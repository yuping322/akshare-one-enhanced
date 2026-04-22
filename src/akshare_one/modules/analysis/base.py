from ..core.base import BaseProvider
from ..core.factory import BaseFactory
import pandas as pd


class AnalysisProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "analysis"


class AnalysisFactory(BaseFactory[AnalysisProvider]):
    _providers: dict[str, type[AnalysisProvider]] = {}
