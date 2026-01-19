from __future__ import annotations


__all__ = ('SwitchCurrencyResult',)


from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.common import MoneyValue


class SwitchCurrencyResult(FunPayObject):
    switched: bool = False
    rate: MoneyValue | None = None
