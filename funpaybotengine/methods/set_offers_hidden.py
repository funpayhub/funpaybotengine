from __future__ import annotations


__all__ = ('SetOffersHidden',)


from typing import TYPE_CHECKING, Any

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.client.session.base import RawResponse


class SetOffersHidden(FunPayMethod[bool]):
    """
    Update offers hidden status (``https://funpay.com/trade/tradeLockSettings``).

    Returns ``True``.
    """

    hidden: bool
    """Offers hidden status."""

    def __init__(self, hidden: bool):
        super().__init__(
            url='trade/tradeLockSettings',
            method=HTTPMethod.POST,
            data=make_data,
            headers={'X-Requested-With': 'XMLHttpRequest'},
            allow_anonymous=False,
            allow_uninitialized=False,
            hidden=hidden,
        )

    async def parse_result(self, response: RawResponse[Any]) -> bool:
        return True

    async def transform_result(self, parsing_result: Any, response: RawResponse[Any]) -> bool:
        return True


async def make_data(method: SetOffersHidden, bot: Bot) -> dict[str, Any]:
    return {
        'userId': bot.userid,
        'mode': int(method.hidden),
    }
