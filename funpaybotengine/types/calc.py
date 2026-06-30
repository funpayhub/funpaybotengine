from __future__ import annotations


__all__ = ('CalcResult', 'MethodResult')


from typing import Any

from pydantic import Field, BaseModel, AliasChoices, field_validator
from funpayparsers.parsers import MoneyValueParser

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import Currency
from funpaybotengine.types.common import MoneyValue


class MethodResult(FunPayObject, BaseModel):
    """
    Represents a result of offer price calculation method (`lots/calc`) for a single
    payment method.
    """

    name: str = ''
    """Payment method name."""

    price: float = 0
    """Calculated price."""

    unit: str
    """Price currency character."""

    pos: int = Field(default=0, validation_alias=AliasChoices('pos', 'sort'))

    @field_validator('price', mode='before')
    @classmethod
    def _validate_price(cls, value: Any) -> float:
        if isinstance(value, str):
            normalized = value.replace(' ', '').replace(',', '.')
            return float(normalized)
        return float(value)

    @property
    def price_money_value(self) -> MoneyValue:
        return MoneyValue(
            raw_source=f'{self.price}{self.unit}', value=self.price, character=self.unit
        )

    @property
    def currency(self) -> Currency:
        return Currency.from_character(self.unit)


class CalcResult(FunPayObject, BaseModel):
    """Represents a result of offer price calculation method (`lots/calc`)."""

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
