from __future__ import annotations


__all__ = ('WithdrawCalcResult',)


from typing import Any

from pydantic import BaseModel, field_validator

from funpaybotengine.types.base import FunPayObject


class WithdrawCalcResult(FunPayObject, BaseModel):
    """
    Represents a result of a withdrawal amount calculation method (``withdraw/calc``).

    FunPay calculates only the amount that was **not** passed in the request:
    if ``amount_int`` is passed, ``amount_ext`` is calculated, and vice versa.

    The field that was passed in the request is not present in the response,
    and therefore is always ``None``.
    """

    amount_int: float | None = None
    """Amount debited from the FunPay balance, if calculated."""

    amount_ext: float | None = None
    """Amount credited to the wallet (i.e. fee already deducted), if calculated."""

    @field_validator('amount_int', 'amount_ext', mode='before')
    @classmethod
    def _validate_amount(cls, value: Any) -> float | None:
        if value is None or value == '':
            return None
        if isinstance(value, str):
            normalized = value.replace('\xa0', '').replace(' ', '').replace(',', '.')
            return float(normalized)
        return float(value)
