from __future__ import annotations


__all__ = ['WithdrawCalc']

import json
from typing import TYPE_CHECKING, Any

from pydantic import model_validator
from typing_extensions import Self

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod
from funpaybotengine.types.withdraw import WithdrawCalcResult


if TYPE_CHECKING:
    from funpaybotengine.client import Bot, RawResponse


def make_data(m: WithdrawCalc, bot: Bot) -> dict[str, Any]:
    # The amount that has to be calculated is not sent at all — that is exactly how the
    # withdrawal form behaves: the field the user is not editing is dropped from the
    # request body, and FunPay returns it in the response.
    amount_field = 'amount_int' if m.amount_int is not None else 'amount_ext'
    amount_value = m.amount_int if m.amount_int is not None else m.amount_ext

    return {
        'preview': '1',
        'currency_id': m.currency_id,
        'ext_currency_id': m.ext_currency_id,
        'wallet': m.wallet,
        amount_field: amount_value,
    }


class WithdrawCalc(FunPayMethod[WithdrawCalcResult]):
    """
    Calculate a withdrawal amount (``https://funpay.com/withdraw/calc``).

    Exactly one of ``amount_int`` / ``amount_ext`` must be specified:
    FunPay calculates the other one and returns it.

    Returns ``funpaybotengine.types.WithdrawCalcResult`` obj.
    """

    url = 'withdraw/calc'
    method = HTTPMethod.POST
    data = make_data
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    model_to_build = WithdrawCalcResult

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
