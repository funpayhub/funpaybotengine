from __future__ import annotations


__all__ = ('MuteChat',)

from typing import TYPE_CHECKING, Any

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import RawResponse


class MuteChat(FunPayMethod[bool]):
    chat_id: int
    mute: bool

    def __init__(
        self,
        chat_id: int,
        mute: bool,
    ) -> None:
        super().__init__(
            url='chat/mute',
            method=HTTPMethod.POST,
            expected_status_codes=[200],
            headers={'X-Requested-With': 'XMLHttpRequest'},
            data={'node_id': chat_id, 'mute': int(mute)},
            allow_anonymous=False,
            allow_uninitialized=False,
            chat_id=chat_id,
            mute=mute,
        )

    async def parse_result(self, response: RawResponse[bool]) -> bool:
        return True

    async def transform_result(self, parsing_result: Any, response: RawResponse[bool]) -> bool:
        return True
