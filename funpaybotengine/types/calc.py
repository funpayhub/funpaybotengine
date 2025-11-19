from __future__ import annotations


__all__ = ('CalcResult', 'MethodResult')


from pydantic import BaseModel, field_validator, Field
from typing import Any

from funpaybotengine.types.enums import Currency
from funpaybotengine.types.common import MoneyValue

from funpayparsers.parsers import MoneyValueParser

import re

class MethodResult(BaseModel):
    """Represents a result of a calculation method."""

    name: str = ""
    price: float = 0

    currency: Currency = Field(
        default=Currency.UNKNOWN,
        validation_alias=("currency", "unit"),
    )

    pos: int = Field(
        default=0,
        validation_alias=("pos", "sort"),
    )

    @field_validator("currency", mode="before")
    def _validate_currency(cls, value: Any) -> Currency:
        if value is None:
            return Currency.UNKNOWN

        if isinstance(value, str):
            return Currency.get_by_character(value)
        
        return value

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
