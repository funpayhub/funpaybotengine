from __future__ import annotations


__all__ = ['GetChatHistory']

import json
from typing import TYPE_CHECKING, Any

from funpayparsers.types import Message as ParserMessage
from funpayparsers.parsers import MessagesParser

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod
from funpaybotengine.types.messages import Message


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class GetChatHistory(FunPayMethod[list[Message]]):
    """
    Get chat history method (``https://funpay.com/chat/history``).

    Returns max. 50 messages before ``before_message_id``.
    """

    url = 'chat/history'
    method = HTTPMethod.GET
    data = lambda m, *_: {'node': str(m.chat_id), 'last_message': str(m.last_message_id)}
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    context = lambda m, *_: {'chat_id' if isinstance(m.chat_id, int) else 'chat_name': m.chat_id}
    allow_anonymous = True
    allow_uninitialized = True

    chat_id: int | str
    """Chat ID."""

    before_message_id: int = 999999999999999999
    """
    Message ID to paginate history **backwards from** (exclusive).

    Messages with IDs **less than** this one will be returned,
    i.e. history will be fetched in reverse order *before* this message.

    Defaults to ``999999999999999999``
    """

    async def parse_result(self, response: RawResponse[Any]) -> list[ParserMessage]:
        return MessagesParser(
            '\n'.join(i['html'] for i in json.loads(response.raw_response)['chat']['messages'])
        ).parse()

    async def transform_result(
        self, parsing_result: list[ParserMessage], response: RawResponse[Any]
    ) -> list[Message]:
        context = await self.get_full_context(response)
        return [Message.model_validate(i, context=context) for i in parsing_result]
