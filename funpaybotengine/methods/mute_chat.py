from __future__ import annotations


__all__ = ['MuteChat']

from typing import TYPE_CHECKING, Any

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import RawResponse


class MuteChat(FunPayMethod[bool]):
    url = 'chat/mute'
    method = HTTPMethod.POST
    data = lambda m, *_: {'node_id': m.chat_id, 'mute': int(m.mute)}
    headers = {'X-Requested-With': 'XMLHttpRequest'}

    chat_id: int
    mute: bool

    async def parse_result(self, response: RawResponse[bool]) -> bool:
        return True

    async def transform_result(self, parsing_result: Any, response: RawResponse[bool]) -> bool:
        return True
