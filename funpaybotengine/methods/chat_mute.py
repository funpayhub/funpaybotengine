from __future__ import annotations


__all__ = ('ChatMute',)

from typing import TYPE_CHECKING, Any

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import Bot, RawResponse


class ChatMute(FunPayMethod[bool]):
    node_id: int
    mute: bool

    __model_to_build__ = bool

    def __init__(
        self,
        node_id: int,
        mute: bool,
    ) -> None:
        super().__init__(
            url='chat/mute',
            method=HTTPMethod.POST,
            expected_status_codes=[200],
            headers={'X-Requested-With': 'XMLHttpRequest'},
            data=make_data,
            allow_anonymous=False,
            allow_uninitialized=False,
            node_id=node_id,
            mute=mute,
        )

    async def parse_result(self, response: RawResponse[bool]) -> bool:
        return True


async def make_data(method: ChatMute, bot: Bot) -> dict[str, Any]:
    return {'node_id': method.node_id, 'mute': int(method.mute)}
