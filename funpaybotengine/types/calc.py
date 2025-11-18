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
        default=Currency.RUB,
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

        if isinstance(value, Currency):
            return value

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return Currency.UNKNOWN
            
            return Currency.get_by_character(value)

        return Currency.UNKNOWN

    @field_validator("price", mode="before")
    def _validate_price(cls, value: Any) -> float:
        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        try:
            from decimal import Decimal
            if isinstance(value, Decimal):
                return float(value)
        except ImportError:
            pass

        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return 0.0

            raw = raw.replace(" ", "").replace("\u00a0", "")
            raw = raw.replace(",", ".")
            raw = re.sub(r"[^\d\.\-]", "", raw)

            if not raw:
                return 0.0

            try:
                return float(raw)
            except ValueError:
                raise ValueError(f"Invalid price value: {value!r}")

        raise TypeError(f"Unsupported type for price: {type(value)!r}")

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
