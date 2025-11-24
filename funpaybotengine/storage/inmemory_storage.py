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
        self._sent_by_bot: set[int] = set()

        self._categories: dict[int, Category] = {}
        self._subcategories: dict[SubcategoryType, dict[int, tuple[Subcategory, Category | None]]] = {}

    async def get_chat_preview(self, chat_id: int) -> PrivateChatPreview | None:
        return self._chats.get(chat_id)

    async def get_chat_previews(self, *chat_ids: int) -> list[PrivateChatPreview | None]:
        if chat_ids:
            return [self._chats.get(i) for i in chat_ids]
        return list(self._chats.values())

    async def save_chat_previews(self, *chats: PrivateChatPreview) -> None:
        for i in chats:
            self._chats[i.id] = i

    async def get_order_preview(self, order_id: str) -> OrderPreview | None:
        return self._orders.get(order_id)

    async def get_order_previews(self, *order_ids: str) -> list[OrderPreview | None]:
        if order_ids:
            return [self._orders.get(i) for i in order_ids]
        return list(self._orders.values())

    async def save_order_previews(self, *orders: OrderPreview) -> None:
        for i in orders:
            self._orders[i.id] = i

    async def get_category(self, category_id: int) -> Category | None:
        return self._categories.get(category_id)

    async def get_categories(self, *category_ids: int) -> list[Category | None]:
        if category_ids:
            return [self._categories.get(i) for i in category_ids]
        return list(self._categories.values())

    async def save_categories(self, *categories: Category) -> None:
        for category in categories:
            self._categories[category.id] = category

            for subcat in category.subcategories:
                inner = self._subcategories.setdefault(subcat.type, {})

                existing = inner.get(subcat.id)
                if existing:
                    old_subcat, old_category = existing
                    if old_subcat != subcat or old_category != category:
                        inner[subcat.id] = (subcat, category)
                else:
                    inner[subcat.id] = (subcat, category)

    async def get_subcategory(
        self,
        subcategory_type: SubcategoryType,
        subcategory_id: int,
    ) -> Subcategory | None:
        res = self._subcategories.get(subcategory_type, {}).get(subcategory_id)
        return res[0] if res else None

    async def get_subcategories(
        self,
        subcategory_type: SubcategoryType,
        *subcategory_ids: int,
    ) -> list[Subcategory | None]:
        inner = self._subcategories.get(subcategory_type, {})
        res = []
        if subcategory_ids:
            for i in subcategory_ids:
                subcat = inner.get(i)
                res.append(subcat[0] if subcat else None)
        else:
            res = [inner[i][0] for i in inner]
        return res

    async def save_subcategories(self, subcategory: Subcategory) -> None: ...

    async def mark_message_as_sent_by_bot(self, message_id: int, by_bot: bool = True) -> None:
        if by_bot:
            self._sent_by_bot.add(message_id)
        else:
            self._sent_by_bot.discard(message_id)

    async def is_message_sent_by_bot(self, message_id: int) -> bool:
        return message_id in self._sent_by_bot
