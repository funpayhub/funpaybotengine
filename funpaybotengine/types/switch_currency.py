from __future__ import annotations


__all__ = ('SwitchCurrencyResult',)


from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import Currency


class SwitchCurrencyResult(FunPayObject):
    switched: bool = False
    rate: float | None = None
    currency_from: Currency = Currency.UNKNOWN
    currency_to: Currency = Currency.UNKNOWN
