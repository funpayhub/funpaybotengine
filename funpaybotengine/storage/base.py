from __future__ import annotations


__all__ = ('Storage',)

from abc import ABC, abstractmethod

from funpaybotengine.types import Subcategory
from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.orders import OrderPreview
from funpaybotengine.types.enums import SubcategoryType


class Storage(ABC):
    @abstractmethod
    async def get_chat_preview(self, chat_id: int) -> PrivateChatPreview | None:
        """
        Retrieves single chat preview.

        :param chat_id: Chat ID.
        """
        ...

    @abstractmethod
    async def get_chat_previews(self, *chat_ids: int | str) -> list[PrivateChatPreview | None]:
        """
        Retrieves multiple chat previews. If `chat_ids` not specified, all saved chat previews
        will be returned.

        :param chat_ids: Chat IDs. If not specified, returns all saved chats.
        """
        ...

    @abstractmethod
    async def save_chat_previews(self, *chats: PrivateChatPreview) -> None:
        """
        Saves provided chat previews.

        :param chats: Chat previews to save.
        """
        ...

    @abstractmethod
    async def get_order_preview(self, order_id: str) -> OrderPreview | None:
        """
        Retrieves single order preview.

        :param order_id: Order ID.
        """
        ...

    @abstractmethod
    async def get_order_previews(self, *order_ids: str) -> list[OrderPreview | None]:
        """
        Retrieves multiple order previews. If `order_ids` not specified, all saved order previews
        will be returned.

        :param order_ids: Chat IDs. If not specified, returns all saved chats.
        """
        ...

    @abstractmethod
    async def save_order_previews(self, *orders: OrderPreview) -> None:
        """
        Saves provided order previews.

        :param orders: Order previews to save.
        """
        ...

    @abstractmethod
    async def get_subcategory(
        self,
        subcategory_type: SubcategoryType,
        subcategory_id: int
    ) -> Subcategory | None:
        """
        Retrieves single subcategory.

        :param subcategory_type: Subcategory type.
        :param subcategory_id: Subcategory ID.
        """
        ...

    @abstractmethod
    async def get_subcategories(
        self,
        subcategory_type: SubcategoryType,
        *subcategory_ids: int,
    ) -> list[Subcategory | None]:
        """
        Retrieves multiple subcategories.

        :param subcategory_type: Subcategory type.
        :param subcategory_ids: Subcategory IDs. If not specified,
        all saved subcategories of specified type will be returned.
        """
        ...

    @abstractmethod
    async def save_subcategories(self, subcategory: Subcategory) -> None:
        """
        Saves provided subcategories.

        :param subcategory: Subcategories to save.
        """
        ...

    @abstractmethod
    async def mark_message_as_sent_by_bot(self, message_id: int, by_bot: bool = True) -> None:
        """
        Marks message with `message_id` as sent by bot.

        :param message_id: Message ID to mark.
        :param by_bot: Whether is message sent by bot or not.
        """
        ...

    @abstractmethod
    async def is_message_sent_by_bot(self, message_id: int) -> bool:
        """
        Returns `True` if message with `message_id` is sent by bot.

        :param message_id: Message ID to check.
        :return: `True` if message with `message_id` is sent by bot, otherwise - `False`.
        """
        ...