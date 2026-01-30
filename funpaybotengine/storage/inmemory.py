from __future__ import annotations

from collections import defaultdict

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
        self._subcategories: dict[SubcategoryType, dict[int, tuple[Subcategory, Category]]] = (
            defaultdict(dict)
        )

    async def get_chat_preview(self, chat_id: int) -> PrivateChatPreview | None:
        return self._chats.get(chat_id)

    async def get_chat_previews(self, *chat_ids: int) -> list[PrivateChatPreview | None]:
        if chat_ids:
            return [self._chats.get(i) for i in chat_ids]
        return list(self._chats.values())

    async def save_chat_previews(self, *chats: PrivateChatPreview) -> None:
        for i in chats:
            self._chats[i.id] = i

    async def remove_chat_previews(self, *chat_ids: int) -> None:
        if chat_ids:
            for i in chat_ids:
                self._chats.pop(i, None)
        else:
            self._chats = {}

    async def get_order_preview(self, order_id: str) -> OrderPreview | None:
        return self._orders.get(order_id)

    async def get_order_previews(self, *order_ids: str) -> list[OrderPreview | None]:
        if order_ids:
            return [self._orders.get(i) for i in order_ids]
        return list(self._orders.values())

    async def save_order_previews(self, *orders: OrderPreview) -> None:
        for i in orders:
            self._orders[i.id] = i

    async def remove_order_previews(self, *order_ids: str) -> None:
        if order_ids:
            for i in order_ids:
                self._orders.pop(i, None)
        else:
            self._orders = {}

    async def get_category(self, category_id: int) -> Category | None:
        return self._categories.get(category_id)

    async def get_categories(self, *category_ids: int) -> list[Category | None]:
        if category_ids:
            return [self._categories.get(i) for i in category_ids]
        return list(self._categories.values())

    async def save_categories(self, *categories: Category) -> None:
        for category in categories:
            self._categories[category.id] = category
        self._update_subcategories()

    async def remove_categories(self, *category_ids: int) -> None:
        if category_ids:
            for i in category_ids:
                self._categories.pop(i, None)
            self._update_subcategories()
        else:
            self._categories = {}
            self._subcategories = defaultdict(dict)

    def _update_subcategories(self) -> None:
        total_dict: dict[SubcategoryType, dict[int, tuple[Subcategory, Category]]] = defaultdict(
            dict,
        )
        for cat in self._categories.values():
            for subcat in cat.subcategories:
                total_dict[subcat.type][subcat.id] = (subcat, cat)
        self._subcategories = total_dict

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

    async def save_subcategories(self, *subcategories: Subcategory) -> None:
        # Slow method is acceptable:
        # FunPay has only ~200 categories and ~3000 subcategories
        # Categories/subcategories update should perform automatically by bot every 10-20 mins
        # and should not perform manually.

        to_replace: dict[Category, list[Subcategory]] = defaultdict(list)

        for new_subcategory in subcategories:
            if not self._subcategories[new_subcategory.type].get(new_subcategory.id):
                continue
            cat = self._subcategories[new_subcategory.type][new_subcategory.id][1]
            to_replace[cat].append(new_subcategory)

        for cat, replacements in to_replace.items():
            to_replace_ordered: dict[SubcategoryType, dict[int, Subcategory]] = defaultdict(dict)
            # {SubcategoryType: {SubcategoryID: Subcategory obj}}
            for i in replacements:
                to_replace_ordered[i.type][i.id] = i

            new_cat = cat.model_copy(
                update={
                    'subcategories': tuple(
                        old_sc
                        if old_sc.id not in to_replace_ordered[old_sc.type]
                        else to_replace_ordered[old_sc.type][old_sc.id]
                        for old_sc in cat.subcategories
                    ),
                },
            )
            self._categories[new_cat.id] = new_cat
        self._update_subcategories()

    async def remove_subcategories(
        self,
        subcategory_type: SubcategoryType,
        *subcategory_ids: int,
    ) -> None:
        # Slow method is acceptable:
        # FunPay has only ~200 categories and ~3000 subcategories
        # Categories/subcategories update should perform automatically by bot every 10-20 mins
        # and should not perform manually.

        ids = subcategory_ids or self._subcategories[subcategory_type].keys()
        to_remove: dict[Category, set[int]] = defaultdict(set)

        for i in ids:
            data = self._subcategories[subcategory_type].get(i)
            if not data:
                continue

            cat = self._subcategories[subcategory_type][i][1]
            to_remove[cat].add(i)

        for cat, ids_to_remove in to_remove.items():
            new_cat = cat.model_copy(
                update={
                    'subcategories': tuple(
                        old_sc
                        for old_sc in cat.subcategories
                        if old_sc.type != subcategory_type or old_sc.id not in ids_to_remove
                    ),
                },
            )
            self._categories[new_cat.id] = new_cat
        self._update_subcategories()

    async def mark_message_as_sent_by_bot(self, message_id: int, by_bot: bool = True) -> None:
        if by_bot:
            self._sent_by_bot.add(message_id)
        else:
            self._sent_by_bot.discard(message_id)

    async def is_message_sent_by_bot(self, message_id: int) -> bool:
        return message_id in self._sent_by_bot
