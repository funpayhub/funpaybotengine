from __future__ import annotations


__all__ = ('Storage',)


from abc import ABC, abstractmethod

from funpaybotengine.types import Category, Subcategory
from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.enums import SubcategoryType
from funpaybotengine.types.orders import OrderPreview


class Storage(ABC):
    @abstractmethod
    async def get_chat_preview(self, chat_id: int) -> PrivateChatPreview | None:
        """
        Retrieve a single chat preview.

        :param chat_id: Chat ID.
        :returns: Chat preview, or ``None`` if not found.
        """
        ...

    @abstractmethod
    async def get_chat_previews(self, *chat_ids: int) -> list[PrivateChatPreview | None]:
        """
        Retrieve multiple chat previews.

        If no ``chat_ids`` are provided, all saved chat previews are returned.

        :param chat_ids: Chat IDs.
        :returns: List of chat previews or ``None`` for missing entries.
        """
        ...

    @abstractmethod
    async def save_chat_previews(self, *chats: PrivateChatPreview) -> None:
        """
        Save provided chat previews.

        :param chats: Chat previews to save.
        """
        ...

    @abstractmethod
    async def remove_chat_previews(self, *chat_ids: int) -> None:
        """
        Removes chat previews with provided chat IDs. If no chat IDs are provided,
        removes all chat previews.

        :param chat_ids: Chat IDs to remove. If not provided, all saved chat previews are removed.
        """

    @abstractmethod
    async def get_order_preview(self, order_id: str) -> OrderPreview | None:
        """
        Retrieve a single order preview.

        :param order_id: Order ID.
        :returns: Order preview, or ``None`` if not found.
        """
        ...

    @abstractmethod
    async def get_order_previews(self, *order_ids: str) -> list[OrderPreview | None]:
        """
        Retrieve multiple order previews.

        If no ``order_ids`` are provided, all saved order previews are returned.

        :param order_ids: Order IDs.
        :returns: List of order previews or ``None`` for missing entries.
        """
        ...

    @abstractmethod
    async def save_order_previews(self, *orders: OrderPreview) -> None:
        """
        Save provided order previews.

        :param orders: Order previews to save.
        """
        ...

    @abstractmethod
    async def remove_order_previews(self, *order_ids: str) -> None:
        """
        Removes order previews with provided order IDs. If no order IDs are provided,
        removes all order previews.

        :param order_ids: Order IDs to remove. If not provided,
        all saved order previews are removed.
        """

    @abstractmethod
    async def get_category(self, category_id: int) -> Category | None:
        """
        Retrieve a single category.

        :param category_id: Category ID.
        :returns: Category, or ``None`` if not found.
        """
        ...

    @abstractmethod
    async def get_categories(self, *category_ids: int) -> list[Category | None]:
        """
        Retrieve multiple categories.

        If no ``category_ids`` are provided, all saved categories are returned.

        :param category_ids: Category IDs.
        :returns: List of categories or ``None`` for missing entries.
        """
        ...

    @abstractmethod
    async def save_categories(self, *categories: Category) -> None:
        """
        Save provided categories.

        :param categories: Categories to save.
        """
        ...

    @abstractmethod
    async def remove_categories(self, *category_ids: int) -> None:
        """
        Removes categories with provided category IDs. If no category IDs are provided,
        removes all categories.

        :param category_ids: Category IDs to remove. If not provided,
        all saved categories are removed.
        """

    @abstractmethod
    async def get_subcategory(
        self,
        subcategory_type: SubcategoryType,
        subcategory_id: int,
    ) -> Subcategory | None:
        """
        Retrieve a single subcategory.

        :param subcategory_type: Subcategory type.
        :param subcategory_id: Subcategory ID.
        :returns: Subcategory, or ``None`` if not found.
        """
        ...

    @abstractmethod
    async def get_subcategories(
        self,
        subcategory_type: SubcategoryType,
        *subcategory_ids: int,
    ) -> list[Subcategory | None]:
        """
        Retrieve multiple subcategories.

        If no ``subcategory_ids`` are provided, all subcategories
        of the given type are returned.

        :param subcategory_type: Subcategory type.
        :param subcategory_ids: Subcategory IDs.
        :returns: List of subcategories or ``None`` for missing entries.
        """
        ...

    @abstractmethod
    async def save_subcategories(self, subcategory: Subcategory) -> None:
        """
        Save the provided subcategory.

        :param subcategory: Subcategory to save.
        """
        ...

    @abstractmethod
    async def remove_subcategories(
        self,
        subcategory_type: SubcategoryType,
        *subcategory_ids: int,
    ) -> None:
        """
        Removes subcategories with provided subcategory type and subcategory IDs.
        If no subcategory IDs are provided, all saved subcategories are removed.


        :param subcategory_type: Subcategory type to remove.
        :param subcategory_ids: Subcategory IDs to remove. If not provided,
        all saved subcategories of provided subcategory type are removed.
        """

    @abstractmethod
    async def mark_message_as_sent_by_bot(self, message_id: int, by_bot: bool = True) -> None:
        """
        Mark a message as sent by the bot.

        :param message_id: Message ID to mark.
        :param by_bot: Whether the message was sent by the bot.
        """
        ...

    @abstractmethod
    async def is_message_sent_by_bot(self, message_id: int) -> bool:
        """
        Check whether a message was sent by the bot.

        :param message_id: Message ID.
        :returns: ``True`` if the message was sent by the bot, otherwise ``False``.
        """
        ...
