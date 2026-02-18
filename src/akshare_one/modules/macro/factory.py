"""
Factory for creating macro economic data providers.
"""

from ..factory_base import BaseFactory
from .base import MacroProvider
from .official import OfficialMacroProvider
from .sina import SinaMacroProvider


class MacroFactory(BaseFactory[MacroProvider]):
    """Factory class for creating macro economic data providers."""

    _providers: dict[str, type[MacroProvider]] = {
        "official": OfficialMacroProvider,
        "sina": SinaMacroProvider,
    }
