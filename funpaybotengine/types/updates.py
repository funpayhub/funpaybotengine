from __future__ import annotations


__all__ = (
    'OrdersCounters',
    'ChatBookmarks',
    'ChatCounter',
    'NodeInfo',
    'ChatNode',
    'ActionResponse',
    'RunnerResponseObject',
    'RunnerResponse',
)

import time
from typing import Any, Generic, Literal, TypeVar
from types import MappingProxyType
from collections.abc import Mapping

from pydantic import BaseModel, ValidationInfo, field_validator

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.enums import RunnerDataType
from funpaybotengine.types.common import CurrentlyViewingOfferInfo
from funpaybotengine.types.messages import Message


UpdateData = TypeVar('UpdateData')


# ------ Simple objects ------
class OrdersCounters(FunPayObject, BaseModel):
    """Represents an order counters data from runner response."""

    purchases: int
    """Active purchases amount."""
    sales: int
    """Active sales amount."""


class ChatBookmarks(FunPayObject, BaseModel):
    """Represents a chat bookmarks data from runner response."""

    counter: int
    """Unread chats amount."""

    latest_message_id: int
    """
    ID of the latest unread message.

    If there are new messages in multiple chats, 
    this field contains the ID of the most recent message among all of them.
    """

    order: list[int]
    """Order of chat previews (list of chats IDs)."""

    chat_previews: list[PrivateChatPreview]
    """List of chat previews."""


class ChatCounter(FunPayObject, BaseModel):
    """Represents a chat counter data from runner response."""

    counter: int
    """Unread chats amount."""

    latest_message_id: int
    """
    ID of the latest unread message.

    If there are new messages in multiple chats, 
    this field contains the ID of the most recent message among all of them.
    """


# ------ Nodes ------
class NodeInfo(FunPayObject, BaseModel):
    """Represents a chat info in chat data from runner response."""

    id: int
    """Chat ID."""

    name: str
    """Chat name."""

    silent: bool
    """Purpose is unknown."""  # todo


class ChatNode(FunPayObject, BaseModel):
    """Represents a chat data from runner response."""

    node: NodeInfo
    """Chat info."""

    messages: list[Message]
    """List of messages."""

    has_history: bool
    """Purpose is unknown."""  # todo


# ------ Response to action ------
class ActionResponse(FunPayObject, BaseModel):
    """Represents an action response data from runner response."""

    error: str | None
    """Error text, if an error occurred while processing a request."""


# ------ Update obj ------
class RunnerResponseObject(FunPayObject, BaseModel, Generic[UpdateData]):
    """Represents a single runner response object from runner response."""

    type: RunnerDataType
    """Object type."""

    id: int | str
    """Related ID (user ID / chat ID / etc)."""

    tag: str
    """Runner tag."""

    data: UpdateData | Literal[False]
    """Runner object data."""


class RunnerResponse(FunPayObject, BaseModel):
    """Represents a runner response."""

    orders_counters: RunnerResponseObject[OrdersCounters] | None
    """Orders counters data."""

    chat_counter: RunnerResponseObject[ChatCounter] | None
    """Chat counter data."""

    chat_bookmarks: RunnerResponseObject[ChatBookmarks] | None
    """Chat bookmarks data."""

    cpu: tuple[RunnerResponseObject[CurrentlyViewingOfferInfo], ...] | None
    """Currently viewing offer info."""

    nodes: tuple[RunnerResponseObject[ChatNode], ...] | None
    """Nodes data."""

    unknown_objects: tuple[Mapping[str, Any], ...] | None
    """Datas with unknown type."""

    response: ActionResponse | None
    """Action response."""

    timestamp: int = None  # type: ignore  # before validator self.get_timestamp returns value
    """Runner response timestamp (UTC)."""

    @field_validator('unknown_objects', mode='before')
    @classmethod
    def convert_to_immutable(cls, value: Any) -> tuple[MappingProxyType[str, Any], ...] | None:
        if value is None:
            return value

        return tuple(MappingProxyType(i) for i in value)

    @field_validator('timestamp', mode='before')
    @classmethod
    def get_timestamp(cls, value: Any, info: ValidationInfo) -> int:
        if not isinstance(info.context, dict) or 'response_timestamp' not in info.context:
            return int(time.time())
        return int(info.context['response_timestamp'])
