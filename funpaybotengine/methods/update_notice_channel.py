from __future__ import annotations


__all__ = ['UpdateNoticeChannel']


from typing import TYPE_CHECKING, Any

from funpaybotengine.types.enums import NoticeChannel
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class UpdateNoticeChannel(FunPayMethod[bool]):
    """
    Update notification channel status (``https://funpay.com/account/noticeChannel``).

    Returns ``True``.
    """
    url = 'account/noticeChannel'
    method = HTTPMethod.POST
    data = lambda m, *_: {'channel': m.value, 'active': int(m.enabled)}
    headers = {'X-Requested-With': 'XMLHttpRequest'}

    channel: NoticeChannel
    """Notification channel."""

    enabled: bool
    """Notification channel active status."""

    async def parse_result(self, response: RawResponse[Any]) -> bool:
        return True

    async def transform_result(self, parsing_result: Any, response: RawResponse[Any]) -> bool:
        return True
