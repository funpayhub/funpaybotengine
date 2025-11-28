from __future__ import annotations


__all__ = (
    'MessageTextFilter',
    'MessageSenderUsernameFilter',
    'MessageSenderIDFilter',
    'MessageHasImageFilter',
    'MessageTypeFilter',
)


from typing import TYPE_CHECKING

from funpaybotengine.types.enums import MessageType

from .base import Filter


if TYPE_CHECKING:
    from funpaybotengine.types.messages import Message
    from funpaybotengine.dispatching.events.base import Event


class MessageTextFilter(Filter):
    def __init__(self, message_text: str, /):
        super().__init__()
        self.message_text = message_text

    async def __call__(self, event: Event[Message]) -> bool:
        return self.message_text == event.object.text


class MessageSenderUsernameFilter(Filter):
    def __init__(self, message_sender_username: str, /):
        super().__init__()
        self.message_sender_username = message_sender_username

    async def __call__(self, event: Event[Message]) -> bool:
        return self.message_sender_username == event.object.sender_username


class MessageSenderIDFilter(Filter):
    def __init__(self, sender_id: int, /):
        super().__init__()
        self.sender_id = sender_id

    async def __call__(self, event: Event[Message]) -> bool:
        return self.sender_id == event.object.sender_id


class MessageHasImageFilter(Filter):
    def __init__(self, has_image: bool, /):
        super().__init__()
        self.has_image = has_image

    async def __call__(self, event: Event[Message]) -> bool:
        return bool(event.object.image_url)


class _MessageTypeFilter(Filter):
    def __init__(self, message_type: MessageType | str, /):
        super().__init__()
        self.message_type = (
            getattr(MessageType, message_type) if isinstance(message_type, str) else message_type
        )

    async def __call__(self, event: Event[Message]) -> bool:
        return event.object.meta.type is self.message_type


class MessageTypeFilter(_MessageTypeFilter):
    NON_SYSTEM = _MessageTypeFilter(MessageType.NON_SYSTEM)
    UNKNOWN_SYSTEM = _MessageTypeFilter(MessageType.UNKNOWN_SYSTEM)
    NEW_ORDER = _MessageTypeFilter(MessageType.NEW_ORDER)
    ORDER_CLOSED = _MessageTypeFilter(MessageType.ORDER_CLOSED)
    ORDER_CLOSED_BY_ADMIN = _MessageTypeFilter(MessageType.ORDER_CLOSED_BY_ADMIN)
    ORDER_REOPENED = _MessageTypeFilter(MessageType.ORDER_REOPENED)
    ORDER_REFUNDED = _MessageTypeFilter(MessageType.ORDER_REFUNDED)
    ORDER_PARTIALLY_REFUNDED = _MessageTypeFilter(MessageType.ORDER_PARTIALLY_REFUNDED)
    NEW_FEEDBACK = _MessageTypeFilter(MessageType.NEW_FEEDBACK)
    FEEDBACK_CHANGED = _MessageTypeFilter(MessageType.FEEDBACK_CHANGED)
    FEEDBACK_DELETED = _MessageTypeFilter(MessageType.FEEDBACK_DELETED)
    NEW_FEEDBACK_REPLY = _MessageTypeFilter(MessageType.NEW_FEEDBACK_REPLY)
    FEEDBACK_REPLY_CHANGED = _MessageTypeFilter(MessageType.FEEDBACK_REPLY_CHANGED)
    FEEDBACK_REPLY_DELETED = _MessageTypeFilter(MessageType.FEEDBACK_REPLY_DELETED)
