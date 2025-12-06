from __future__ import annotations


__all__ = ('GetTelegramConnectURL',)


from typing import TYPE_CHECKING, Any

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class GetTelegramConnectURL(FunPayMethod[str]):
    """
    Get telegram connect url via @funpaysmartbot (``https://funpay.com/account/linkTelegram``).
    """

    def __init__(self) -> None:
        super().__init__(
            url='account/linkTelegram',
            method=HTTPMethod.GET,
            allow_anonymous=False,
            allow_uninitialized=True,
        )

    async def parse_result(self, response: RawResponse[Any]) -> str:
        return response.url

    async def transform_result(self, parsing_result: str, response: RawResponse[Any]) -> str:
        return parsing_result
