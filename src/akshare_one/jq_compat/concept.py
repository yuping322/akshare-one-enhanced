"""
src/akshare_one/jq_compat/concept.py
JQ-compatible concept APIs.
"""

import pandas as pd
import akshare as ak
from functools import lru_cache
from typing import Optional, List, Union
from ..modules.concept import get_concept_list as _get_concept_list_ak
from ..modules.concept import get_concept_stocks as _get_concept_stocks_ak
from ..constants import SYMBOL_ZFILL_WIDTH


def get_concepts(date: Optional[str] = None, df: bool = True) -> Union[pd.DataFrame, dict]:
    """Get concept sector list. JQ-compatible."""
    res = _get_concept_list_ak()
    if res.empty:
        return pd.DataFrame(columns=["code", "name"]) if df else {}

    if "symbol" in res.columns and "code" not in res.columns:
        res = res.rename(columns={"symbol": "code"})

    if not df:
        return res.set_index("code")["name"].to_dict()
    return res[["code", "name"]]


def get_concept_stocks(concept: str, date: Optional[str] = None) -> List[str]:
    """Get stocks in a concept sector. JQ-compatible."""
    res = _get_concept_stocks_ak(concept=concept)
    if res.empty:
        return []

    def format_jq_code(code):
        code = str(code).zfill(SYMBOL_ZFILL_WIDTH)
        if code.startswith("6"):
            return f"{code}.XSHG"
        elif code.startswith("8") or code.startswith("4"):
            return f"{code}.BJ"
        return f"{code}.XSHE"

    code_col = "symbol" if "symbol" in res.columns else "code"
    if code_col in res.columns:
        return res[code_col].apply(format_jq_code).tolist()
    return []


@lru_cache(maxsize=100)
def _get_concept_reverse_mapping():
    """Build a mapping of stock code to concept list."""
    concepts = get_concepts(df=True)
    mapping = {}
    for _, row in concepts.iterrows():
        c_name = row["name"]
        stocks = get_concept_stocks(c_name)
        for s in stocks:
            if s not in mapping:
                mapping[s] = []
            mapping[s].append(c_name)
    return mapping


def get_concept(security: str, date: Optional[str] = None) -> List[str]:
    """Get concepts for a given security. JQ-compatible."""
    # Use the cached reverse mapping for efficiency
    mapping = _get_concept_reverse_mapping()
    return mapping.get(security, [])


def get_all_concepts(date: Optional[str] = None) -> pd.DataFrame:
    """Get all concepts and their component stocks."""
    concepts = get_concepts(date=date, df=True)
    if concepts.empty:
        return pd.DataFrame(columns=["concept_code", "concept_name", "stock_code"])

    results = []
    for _, row in concepts.iterrows():
        c_code = row["code"]
        c_name = row["name"]
        stocks = get_concept_stocks(c_name, date)
        for s in stocks:
            results.append({"concept_code": c_code, "concept_name": c_name, "stock_code": s})
    return pd.DataFrame(results)


# Aliases
get_concepts_jq = get_concepts
get_concept_stocks_jq = get_concept_stocks
get_concept_jq = get_concept

__all__ = [
    "get_concepts",
    "get_concept_stocks",
    "get_concept",
    "get_all_concepts",
    "get_concepts_jq",
    "get_concept_stocks_jq",
    "get_concept_jq",
]
