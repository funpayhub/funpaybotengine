from __future__ import annotations


__all__ = ('Get2faStatus',)

from typing import TYPE_CHECKING

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import RawResponse


class Get2faStatus(FunPayMethod[bool]):
    url = 'security/twoFactorSetting'
    method = HTTPMethod.GET

    async def parse_result(self, response: RawResponse[bool]) -> bool:
        lang = response.executed_as.locale.name
        q = 'enable 2fa' if lang == 'EN' else 'увімкнути 2fa' if lang == 'UK' else 'включить 2fa'
        return q not in response.raw_response.lower()

    async def transform_result(self, parsing_result: bool, response: RawResponse[bool]) -> bool:
        return parsing_result
