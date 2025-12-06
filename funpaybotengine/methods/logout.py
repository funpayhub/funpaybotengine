from __future__ import annotations


__all__ = ('Logout',)


from typing import TYPE_CHECKING, Any

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class Logout(FunPayMethod[bool]):
    """
    Logout from current account (``https://funpay.com/account/logout``).
    Makes current ``golden_key`` invalid.

    Returns ``True``.
    """

    logout_token: str
    """Logout token."""

    def __init__(self, logout_token: str):
        super().__init__(
            method=HTTPMethod.GET,
            url='account/logout',
            data={'token': logout_token},
            allow_uninitialized=False,
            allow_anonymous=False,
            logout_token=logout_token,
            expected_status_codes=[200, 302],
        )

    async def parse_result(self, response: RawResponse[Any]) -> bool:
        return response.cookies.get('golden_key') == 'deleted'

    async def transform_result(self, parsing_result: bool, response: RawResponse[Any]) -> bool:
        return parsing_result
