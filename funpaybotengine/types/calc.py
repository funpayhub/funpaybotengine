from __future__ import annotations


__all__ = ('CalcResult', 'MethodResult')


from typing import Any

from pydantic import Field, BaseModel, field_validator
from funpayparsers.parsers import MoneyValueParser

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import Currency
from funpaybotengine.types.common import MoneyValue


class MethodResult(FunPayObject, BaseModel):
    """Represents a result of a calculation method."""

    name: str = ''
    price: float = 0
    currency: Currency = Field(default=Currency.UNKNOWN, validation_alias='unit')
    pos: int = Field(default=0, validation_alias='sort')

    @field_validator('currency', mode='before')
    @classmethod
    def _validate_currency(cls, value: Any) -> Currency:
        if isinstance(value, str):
            return Currency.get_by_character(value)
        return Currency.UNKNOWN


class CalcResult(FunPayObject, BaseModel):
    """Represents an answer from calculation request."""

    methods: list[MethodResult] = Field(default_factory=list)
    min_price: MoneyValue | None = None
    error: bool | str | None = None

    @field_validator('min_price', mode='before')
    @classmethod
    def _validate_min_price(cls, value: Any) -> dict[str, Any] | None:
        if value is None:
            return None

        result = MoneyValueParser(value).parse()
        return result.as_dict()
