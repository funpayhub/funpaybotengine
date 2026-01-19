from __future__ import annotations

from funpaybotengine.types.common import MoneyValue


__all__ = ('SwitchCurrency',)

import re
import json
from typing import TYPE_CHECKING

from funpaybotengine.types import Currency, SwitchCurrencyResult
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import RawResponse


class SwitchCurrency(FunPayMethod[SwitchCurrencyResult]):
    currency: Currency
    confirm: bool

    def __init__(
        self,
        currency: Currency,
        confirm: bool,
    ) -> None:
        if currency == Currency.UNKNOWN:
            raise ValueError('currency must be a valid Currency enum value')

        super().__init__(
            url='account/switchCurrency',
            method=HTTPMethod.POST,
            expected_status_codes=[200],
            headers={'X-Requested-With': 'XMLHttpRequest'},
            data={'cy': currency.name.lower(), 'confirmed': confirm},
            allow_anonymous=False,
            allow_uninitialized=False,
            currency=currency,
            confirm=confirm,
        )

    async def parse_result(
        self, response: RawResponse[SwitchCurrencyResult]
    ) -> SwitchCurrencyResult:
        if self.confirm:
            return SwitchCurrencyResult(raw_source=response.raw_response, switched=True, rate=None)

        result = json.loads(response.raw_response)

        if 'modal' not in result:
            return SwitchCurrencyResult(
                raw_source=response.raw_response, switched=False, rate=None
            )

        space = r'(?:\s|&nbsp;|&#160;)+'
        pattern = re.compile(
            rf'(?P<rate>\d+(?:\.\d+)?)'
            rf'{space}(?P<from>[₽$€])'
            rf'{space}(?:за|по|for){space}1{space}(?P<to>[₽$€])',
            re.IGNORECASE,
        )

        match = pattern.search(result['modal'])

        if not match:
            return SwitchCurrencyResult(
                raw_source=response.raw_response, switched=False, rate=None
            )

        rate = float(match.group('rate'))
        from_cur_symbol = match.group('from')

        from_cur = Currency.get_by_character(from_cur_symbol)

        return SwitchCurrencyResult(
            raw_source=response.raw_response,
            rate=MoneyValue(
                raw_source=response.raw_response,
                value=rate,
                character=from_cur,
            ),
        )

    async def transform_result(
        self,
        parsing_result: SwitchCurrencyResult,
        response: RawResponse[SwitchCurrencyResult],
    ) -> SwitchCurrencyResult:
        return parsing_result
