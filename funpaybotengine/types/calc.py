from __future__ import annotations


__all__ = ('CalcResult', 'MethodResult')


from typing import Any

from pydantic import Field, BaseModel, field_validator, model_validator
from funpayparsers.parsers import MoneyValueParser

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.common import MoneyValue


class MethodResult(FunPayObject, BaseModel):
    name: str = ''
    price: MoneyValue
    pos: int = Field(default=0, validation_alias='sort')

    @model_validator(mode='before')
    @classmethod
    def _build_price(cls, values: dict[str, Any]) -> dict[str, Any]:
        raw_price = values.get('price')
        unit = values.get('unit') or values.get('currency')
        if raw_price is None or unit is None:
            return values

        if isinstance(raw_price, (int, float)):
            values['price'] = MoneyValue(
                value=raw_price, character=str(unit), raw_source=f'{raw_price} {unit}'
            )
            return values

        if isinstance(raw_price, str):
            mv = MoneyValueParser(f'{raw_price} {unit}').parse()
            values['price'] = mv.as_dict()
            return values

        return values


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
