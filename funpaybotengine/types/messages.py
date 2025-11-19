from __future__ import annotations


__all__ = ('Message',)


from typing import TYPE_CHECKING, Any, Literal, overload
from io import BytesIO

from pydantic import BaseModel, PrivateAttr, ValidationInfo, field_validator
from funpayparsers.parsers.utils import parse_date_string

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import MessageType
from funpaybotengine.types.common import UserBadge


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.types.chat import Chat
    from funpaybotengine.types.pages.chat_page import ChatPage
    from funpaybotengine.types.pages.profile_page import ProfilePage


class MessageMeta(FunPayObject, BaseModel):
    """
    Represents a message meta info.
    """

    type: MessageType = MessageType.NON_SYSTEM
    """Message type."""

    order_id: str | None = None
    """Mentioned order ID."""

    order_desc: str | None = None
    """Mentioned order description."""

    seller_id: int | None = None
    """Mentioned seller ID."""

    seller_username: str | None = None
    """Mentioned seller username."""

    buyer_id: int | None = None
    """Mentioned buyer ID."""

    buyer_username: str | None = None
    """Mentioned buyer username."""

    admin_id: int | None = None
    """Mentioned admin ID."""

    admin_username: str | None = None
    """Mentioned admin username."""


class Message(FunPayObject, BaseModel):
    """Represents a message from any FunPay chat (private or public)."""

    id: int
    """Unique message ID."""

    is_heading: bool
    """
    Indicates whether this is a heading message.

    Heading messages contain sender information (ID, username, etc.).
    If this is not a heading message, it means the message was sent by the same user
    as the previous one. The parser does not resolve sender data for such messages
    and sets all related fields to ``None``.
    """

    sender_id: int | None
    """Sender ID."""

    sender_username: str | None
    """Sender username."""

    badge: UserBadge | None
    """Sender's badge."""

    send_date_text: str | None
    """Message date (as human-readable text)."""

    text: str | None
    """
    Text content of the message.

    Mutually exclusive with ``Message.image_url``: 
    a message can contain either text or an image, but not both.

    Will be ``None`` if the message contains an image.
    """

    image_url: str | None
    """
    URL of the image in the message.

    Mutually exclusive with ``Message.text``: 
    a message can contain either an image or text, but not both.

    Will be ``None`` if the message contains text.
    """

    chat_id: int | str | None
    """
    Chat ID where the message was sent.

    Parsers obtain this value from the `context` field of the provided options only.

    Context key: ``chat_id``.
    """

    chat_name: str | None
    """
    Chat name where the message was sent.

    This value is available only via the options context during parsing.

    Context key: ``chat_name``.
    """

    meta: MessageMeta
    """
    Message meta info.
    """

    _chat_page: ChatPage | None = PrivateAttr(default=None)
    _sender_profile: ProfilePage | None = PrivateAttr(default=None)

    @property
    def chat_identifier(self) -> int | str | None:
        return self.chat_id or self.chat_name

    @property
    def from_me(self) -> bool:
        if not self.bot:
            return False
        return self.bot.userid == self.sender_id

    @property
    def timestamp(self) -> int:
        if not self.send_date_text:
            return 0
        return parse_date_string(self.send_date_text)

    @overload
    async def reply(
        self,
        text: str | None = None,
        image: str | BytesIO | int | None = None,
        enforce_whitespaces: bool = True,
        keep_chat_unread: Literal[False] = False,
    ) -> Message: ...

    @overload
    async def reply(
        self,
        text: str | None = None,
        image: str | BytesIO | int | None = None,
        enforce_whitespaces: bool = True,
        keep_chat_unread: Literal[True] = True,
    ) -> None: ...

    async def reply(
        self,
        text: str | None = None,
        image: str | BytesIO | int | None = None,
        enforce_whitespaces: bool = True,
        keep_chat_unread: Literal[True] | Literal[False] = False,
    ) -> Message | None:
        assert self.chat_identifier is not None, 'Unable to resolve chat identifier.'

        return await self.get_bound_bot().send_message(
            chat_id=self.chat_identifier,
            text=text,
            image=image,
            enforce_whitespaces=enforce_whitespaces,
            keep_chat_unread=keep_chat_unread,
        )

    async def chat(self, update: bool = False) -> Chat:
        return (await self.chat_page(update=update)).chat  # type: ignore  # will have chat

    async def chat_page(self, update: bool = False) -> ChatPage:
        assert self.chat_identifier is not None, 'Unable to resolve chat identifier.'

        if self._chat_page is not None and not update:
            return self._chat_page

        return await self.get_bound_bot().get_chat_page(
            chat_id=self.chat_identifier,
        )

    async def sender_profile_page(self, update: bool = False) -> ProfilePage:
        assert self.sender_id is not None, 'Unable to resolve sender ID.'

        if self._sender_profile is not None and not update:
            return self._sender_profile

        return await self.get_bound_bot().get_profile_page(id=self.sender_id)

    async def is_sent_by_bot(self) -> bool:
        return await self.get_bound_bot().storage.is_message_sent_by_bot(self.id)

    async def mark_as_sent_by_bot(self, bot: Bot | None = None, by_bot: bool = True) -> None:
        bot = bot or self.get_bound_bot()
        await bot.storage.mark_message_as_sent_by_bot(self.id, by_bot=by_bot)

    @field_validator('chat_id', mode='before')
    @classmethod
    def _get_chat_id_from_context(cls, value: Any, info: ValidationInfo) -> Any:
        if info.context:
            return info.context.get('chat_id') if value is None else value
        return None

    @field_validator('chat_name', mode='before')
    @classmethod
    def _get_chat_name_from_context(cls, value: Any, info: ValidationInfo) -> Any:
        if info.context:
            return info.context.get('chat_name') if value is None else value
        return None
