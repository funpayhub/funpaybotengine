from __future__ import annotations


__all__ = ['SetOffersHidden']


from typing import TYPE_CHECKING, Any

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class SetOffersHidden(FunPayMethod[bool]):
    """
    Update offers hidden status (``https://funpay.com/trade/tradeLockSettings``).

    Returns ``True``.
    """
    url = 'trade/tradeLockSettings'
    method = HTTPMethod.POST
    data = lambda m, bot: {'userId': bot.userid, 'mode': int(m.hidden)}
    headers = {'X-Requested-With': 'XMLHttpRequest'}

    hidden: bool
    """Offers hidden status."""

    async def parse_result(self, response: RawResponse[Any]) -> bool:
        return True

    async def transform_result(self, parsing_result: Any, response: RawResponse[Any]) -> bool:
        return True
