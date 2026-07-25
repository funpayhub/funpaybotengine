from __future__ import annotations


__all__ = ['GetChatPage']


from funpayparsers.parsers.page_parsers import ChatPageParser

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod
from funpaybotengine.types.pages.chat_page import ChatPage


class GetChatPage(FunPayMethod[ChatPage]):
    """
    Get chat method (``https://funpay.com/chat/history``).

    Returns max. 50 messages before ``before_message_id``.
    """

    url = 'chat/'
    method = HTTPMethod.GET
    data = lambda m, *_: {'node': str(m.chat_id)}
    allow_anonymous = True
    allow_uninitialized = True
    parser_cls = ChatPageParser
    model_to_build = ChatPage

    chat_id: int | str
    """Chat ID."""
