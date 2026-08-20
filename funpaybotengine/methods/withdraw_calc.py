from __future__ import annotations


__all__ = ('WithdrawCalc',)


import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod
from funpaybotengine.types.withdraw import WithdrawCalcResult


if TYPE_CHECKING:
    from funpaybotengine.client import Bot, RawResponse


class WithdrawCalc(FunPayMethod[WithdrawCalcResult], BaseModel):
    """
    Calculate a withdrawal amount (``https://funpay.com/withdraw/calc``).

    Exactly one of ``amount_int`` / ``amount_ext`` must be specified:
    FunPay calculates the other one and returns it.

    Returns ``funpaybotengine.types.withdraw.WithdrawCalcResult`` obj.
    """

    currency_id: str
    """Balance currency ID (e.g. ``'rub'``)."""

    ext_currency_id: str
    """Withdrawal method ID (e.g. ``'card_rub'``, ``'fps'``)."""

    wallet: str
    """Card / phone / wallet number to withdraw to."""

    amount_int: float | None = None
    """Amount to debit from the FunPay balance. Mutually exclusive with ``amount_ext``."""

    amount_ext: float | None = None
    """Amount to credit to the wallet. Mutually exclusive with ``amount_int``."""

    __model_to_build__ = WithdrawCalcResult

    def __init__(
        self,
        currency_id: str,
        ext_currency_id: str,
        wallet: str,
        amount_int: float | None = None,
        amount_ext: float | None = None,
        locale: Language | None = None,
    ) -> None:
        super().__init__(
            url='withdraw/calc',
            method=HTTPMethod.POST,
            locale=locale,
            expected_status_codes=[200],
            headers={'X-Requested-With': 'XMLHttpRequest'},
            data=make_data,
            allow_anonymous=False,
            allow_uninitialized=False,
            currency_id=currency_id,
            ext_currency_id=ext_currency_id,
            wallet=wallet,
            amount_int=amount_int,
            amount_ext=amount_ext,
        )

    @model_validator(mode='after')
    def _check_amounts(self) -> Self:
        if (self.amount_int is None) == (self.amount_ext is None):
            raise ValueError(
                'Exactly one of `amount_int` / `amount_ext` must be specified: '
                'FunPay calculates the one that is not passed.',
            )
        return self

    async def parse_result(self, response: RawResponse[WithdrawCalcResult]) -> dict[str, Any]:
        return json.loads(response.raw_response)  # type: ignore # always dict


async def make_data(method: WithdrawCalc, bot: Bot) -> dict[str, Any]:
    # The amount that must be calculated is not passed at all:
    # FunPay returns it in the response.
    amount_field = 'amount_int' if method.amount_int is not None else 'amount_ext'
    amount_value = method.amount_int if method.amount_int is not None else method.amount_ext

    return {
        'preview': '1',
        'currency_id': method.currency_id,
        'ext_currency_id': method.ext_currency_id,
        'wallet': method.wallet,
        amount_field: amount_value,
    }
