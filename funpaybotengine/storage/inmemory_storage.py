from __future__ import annotations

from funpayparsers.types import SubcategoryType

from funpaybotengine.types import Category, Subcategory
from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.storage.base import Storage
from funpaybotengine.types.orders import OrderPreview


__all__ = ('InMemoryStorage',)


class InMemoryStorage(Storage):
    def __init__(self) -> None:
        self._chats: dict[int, PrivateChatPreview] = {}
        self._orders: dict[str, OrderPreview] = {}
        self._categories: dict[int, Category] = {}
        self._subcategories: dict[str, Subcategory] = {}
        self._sent_by_bot: set[int] = set()

    async def get_chat_preview(self, chat_id: int) -> PrivateChatPreview | None:
        return self._chats.get(chat_id, None)

    async def get_chat_previews(self, *chat_ids: int) -> list[PrivateChatPreview | None]:
        return [(self._chats[i] if i in self._chats else None) for i in chat_ids]

    async def save_chat_previews(self, *chats: PrivateChatPreview) -> None:
        for i in chats:
            self._chats[i.id] = i

    async def get_order_preview(self, order_id: str) -> OrderPreview | None:
        return self._orders.get(order_id, None)

    async def get_order_previews(self, *order_ids: str) -> list[OrderPreview | None]:
        return [(self._orders[i] if i in self._orders else None) for i in order_ids]

    async def save_order_previews(self, *orders: OrderPreview) -> None:
        for i in orders:
            self._orders[i.id] = i

    async def get_category(self, category_id: int) -> Category | None:
        raise NotImplementedError()  # todo

    async def get_categories(self, *category_ids: int) -> list[Category | None]:
        raise NotImplementedError()  # todo

    async def save_categories(self, *categories: Category | None) -> None: ...

    async def get_subcategory(
        self,
        subcategory_type: SubcategoryType,
        subcategory_id: int,
    ) -> Subcategory | None:
        raise NotImplementedError()  # todo

    async def get_subcategories(
        self,
        subcategory_type: SubcategoryType,
        *subcategory_ids: int,
    ) -> list[Subcategory | None]:
        raise NotImplementedError()  # todo

    async def save_subcategories(self, subcategory: Subcategory) -> None: ...

    async def mark_message_as_sent_by_bot(self, message_id: int, by_bot: bool = True) -> None:
        if by_bot:
            self._sent_by_bot.add(message_id)
        else:
            self._sent_by_bot.discard(message_id)

    async def is_message_sent_by_bot(self, message_id: int) -> bool:
        return message_id in self._sent_by_bot
