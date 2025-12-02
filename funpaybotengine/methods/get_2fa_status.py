from __future__ import annotations


__all__ = ('Get2faStatus',)

from typing import TYPE_CHECKING

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import RawResponse


class Get2faStatus(FunPayMethod[bool]):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            url='security/twoFactorSetting',
            method=HTTPMethod.GET,
            expected_status_codes=[200],
            allow_anonymous=False,
            allow_uninitialized=False,
        )

    async def parse_result(self, response: RawResponse[bool]) -> bool:
        locale = response.executed_as.locale.name

        if locale == 'EN':
            query = 'enable 2fa'
        elif locale == 'UK':
            query = 'увімкнути 2fa'
        else:
            query = 'включить 2fa'

        return query not in response.raw_response.lower()
