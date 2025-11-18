from __future__ import annotations


__all__ = ('CalcResult', 'MethodResult')


from pydantic import BaseModel, field_validator

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import Currency
from funpaybotengine.types.common import MoneyValue

from funpayparsers.parsers import MoneyValueParser

class MethodResult(BaseModel):
    """Represents a result of a calculation method."""

    name: str = ""
    price: float = 0
    currency: Currency = Currency.RUB
    pos: int = 0

    @field_validator("currency", mode="before")
    def _validate_currency(cls, value: str):
        if value is None:
            return Currency.RUB
        
        return Currency.get_by_character(value)
    
    @field_validator("price", mode="before")
    def _validate_price(cls, value: str):
        if value is None:
            return 0
        
        return float(value.replace(' ', ''))

class CalcResult(BaseModel):
    """Represents an answer from calculation request."""

    methods: list[MethodResult] = []
    min_price: MoneyValue | None = None
    error: bool | str | None = None

    @field_validator("min_price", mode="before")
    def _validate_min_price(cls, value):
        if value is None:
            return None
        
        return MoneyValueParser(value).parse()
