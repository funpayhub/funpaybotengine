from __future__ import annotations

from typing import Any, TypeVar
from enum import Enum

from pydantic import ValidationError
from redis.asyncio import Redis

from funpaybotengine.types import (
    Category,
    Subcategory,
    FunPayObject,
    SubcategoryType,
    PrivateChatPreview,
)
from funpaybotengine.storage.base import Storage
from funpaybotengine.types.orders import OrderPreview


__all__ = ('RedisStorage',)

T = TypeVar('T', bound=FunPayObject)


class StoragePrefix(str, Enum):
    CHAT = 'chat'
    ORDER = 'order'
    CATEGORY = 'category'
    SUBCATEGORY = 'subcategory'
    SENT_BY_BOT = 'sent_by_bot'

    def __str__(self) -> str:
        return self.value


class RedisStorage(Storage):
    def __init__(self, redis: Redis, key: str | None = None) -> None:
        self._redis: Redis = redis
        self._key: str = key or 'funpaybotengine'

    @staticmethod
    def _decode(value: str | bytes) -> str:
        return value.decode() if isinstance(value, bytes) else value

    def _get_key(self, prefix: StoragePrefix) -> str:
        return f'{self._key}:{prefix}'

    def _get_subcategory_key(self, subcategory_type: SubcategoryType, subcategory_id: int) -> str:
        key: str = self._get_key(StoragePrefix.SUBCATEGORY)
        return f'{key}:{subcategory_type.name}:{str(subcategory_id)}'

    async def _get(self, value: str, prefix: StoragePrefix, funpay_object: type[T]) -> T | None:
        name: str = self._get_key(prefix)
        item: str | bytes | None = await self._redis.hget(name, value)

        if item is None:
            return None

        try:
            model: T = funpay_object.model_validate_json(item)
            return model
        except ValidationError:
            return None

    async def _get_all(
        self, *values: str, prefix: StoragePrefix, funpay_object: type[T]
    ) -> list[T | None]:
        name: str = self._get_key(prefix)

        if not values:
            mapping: dict[str | bytes, str | bytes] = await self._redis.hgetall(name)
            raw_data: list[str | bytes] = list(mapping.values())
        else:
            raw_data = await self._redis.hmget(name, list(values))

        if not raw_data:
            return []

        items: list[T | None] = []

        for item in raw_data:
            if item is None:
                items.append(None)
                continue

            try:
                items.append(funpay_object.model_validate_json(item))
            except ValidationError:
                items.append(None)

        return items

    async def _save(self, *funpay_objects: Any, prefix: StoragePrefix) -> None:
        if not funpay_objects:
            return

        name: str = self._get_key(prefix)
        mapping: dict[str, str] = {
            str(item.id): item.model_dump_json()
            for item in funpay_objects
            if getattr(item, 'id', None) is not None
        }

        if not mapping:
            return

        await self._redis.hset(name, mapping=mapping)

    async def _remove(self, *values: str, prefix: StoragePrefix) -> None:
        name: str = self._get_key(prefix)

        if not values:
            await self._redis.delete(name)
            return

        await self._redis.hdel(name, *values)

    async def get_chat_preview(self, chat_id: int) -> PrivateChatPreview | None:
        return await self._get(str(chat_id), StoragePrefix.CHAT, PrivateChatPreview)

    async def get_chat_previews(self, *chat_ids: int) -> list[PrivateChatPreview | None]:
        values: list[str] = [str(chat_id) for chat_id in chat_ids]
        return await self._get_all(
            *values, prefix=StoragePrefix.CHAT, funpay_object=PrivateChatPreview
        )

    async def save_chat_previews(self, *chats: PrivateChatPreview) -> None:
        await self._save(*chats, prefix=StoragePrefix.CHAT)

    async def remove_chat_previews(self, *chat_ids: int) -> None:
        values: list[str] = [str(chat_id) for chat_id in chat_ids]
        await self._remove(*values, prefix=StoragePrefix.CHAT)

    async def get_order_preview(self, order_id: str) -> OrderPreview | None:
        return await self._get(order_id, StoragePrefix.ORDER, OrderPreview)

    async def get_order_previews(self, *order_ids: str) -> list[OrderPreview | None]:
        return await self._get_all(
            *order_ids, prefix=StoragePrefix.ORDER, funpay_object=OrderPreview
        )

    async def save_order_previews(self, *orders: OrderPreview) -> None:
        await self._save(*orders, prefix=StoragePrefix.ORDER)

    async def remove_order_previews(self, *order_ids: str) -> None:
        await self._remove(*order_ids, prefix=StoragePrefix.ORDER)

    async def get_category(self, category_id: int) -> Category | None:
        return await self._get(str(category_id), StoragePrefix.CATEGORY, Category)

    async def get_categories(self, *category_ids: int) -> list[Category | None]:
        values: list[str] = [str(category_id) for category_id in category_ids]
        return await self._get_all(*values, prefix=StoragePrefix.CATEGORY, funpay_object=Category)

    async def save_categories(self, *categories: Category) -> None:
        if not categories:
            return

        category_name: str = self._get_key(StoragePrefix.CATEGORY)
        subcategory_name: str = self._get_key(StoragePrefix.SUBCATEGORY)

        category_mapping: dict[str, str] = {
            str(category.id): category.model_dump_json() for category in categories
        }
        subcategory_mapping: dict[str, str] = {}

        for category in categories:
            for subcategory in category.subcategories:
                key: str = self._get_subcategory_key(subcategory.type, subcategory.id)
                subcategory_mapping[key] = str(category.id)

        await self._redis.hset(category_name, mapping=category_mapping)

        if subcategory_mapping:
            await self._redis.hset(subcategory_name, mapping=subcategory_mapping)

    async def remove_categories(self, *category_ids: int) -> None:
        category_name: str = self._get_key(StoragePrefix.CATEGORY)
        subcategory_name: str = self._get_key(StoragePrefix.SUBCATEGORY)

        if not category_ids:
            await self._redis.delete(category_name, subcategory_name)
            return

        categories: list[Category | None] = await self.get_categories(*category_ids)
        subcategory_keys: list[str] = [
            self._get_subcategory_key(subcategory.type, subcategory.id)
            for category in categories
            if category is not None
            for subcategory in category.subcategories
        ]

        await self._redis.hdel(category_name, *(str(category_id) for category_id in category_ids))

        if subcategory_keys:
            await self._redis.hdel(subcategory_name, *subcategory_keys)

    async def get_subcategory(
        self, subcategory_type: SubcategoryType, subcategory_id: int
    ) -> Subcategory | None:
        subcategory_name: str = self._get_key(StoragePrefix.SUBCATEGORY)
        key: str = self._get_subcategory_key(subcategory_type, subcategory_id)

        category_id_raw: str | bytes | None = await self._redis.hget(subcategory_name, key)
        if category_id_raw is None:
            return None

        category: Category | None = await self.get_category(int(self._decode(category_id_raw)))

        if category is None:
            return None

        for subcategory in category.subcategories:
            if subcategory.id == subcategory_id and subcategory.type == subcategory_type:
                return subcategory
        return None

    async def get_subcategories(
        self, subcategory_type: SubcategoryType, *subcategory_ids: int
    ) -> list[Subcategory | None]:
        if not subcategory_ids:
            categories: list[Category | None] = await self.get_categories()
            return [
                subcategory
                for category in categories
                if category is not None
                for subcategory in category.subcategories
                if subcategory.type == subcategory_type
            ]

        subcategory_name: str = self._get_key(StoragePrefix.SUBCATEGORY)
        keys: list[str] = [
            self._get_subcategory_key(subcategory_type, subcategory_id)
            for subcategory_id in subcategory_ids
        ]

        category_ids_raw: list[str | bytes | None] = await self._redis.hmget(
            subcategory_name, keys
        )
        unique_category_ids: set[int] = {
            int(self._decode(cat_id)) for cat_id in category_ids_raw if cat_id is not None
        }

        if not unique_category_ids:
            return [None] * len(subcategory_ids)

        categories_list: list[Category | None] = await self.get_categories(*unique_category_ids)
        categories_map: dict[int, Category] = {
            category.id: category for category in categories_list if category is not None
        }

        result: list[Subcategory | None] = []
        for subcategory_id, category_id_raw in zip(subcategory_ids, category_ids_raw):
            if category_id_raw is None:
                result.append(None)
                continue

            category = categories_map.get(int(self._decode(category_id_raw)))
            if not category:
                result.append(None)
                continue

            found = None
            for subcategory in category.subcategories:
                if subcategory.id == subcategory_id and subcategory.type == subcategory_type:
                    found = subcategory
                    break
            result.append(found)

        return result

    async def save_subcategories(self, *subcategories: Subcategory) -> None:
        if not subcategories:
            return

        subcategory_name: str = self._get_key(StoragePrefix.SUBCATEGORY)
        keys: list[str] = [
            self._get_subcategory_key(subcategory.type, subcategory.id)
            for subcategory in subcategories
        ]

        category_ids_raw: list[str | bytes | None] = await self._redis.hmget(
            subcategory_name, keys
        )

        category_to_subcategories: dict[int, list[Subcategory]] = {}
        for subcategory, category_id_raw in zip(subcategories, category_ids_raw):
            if category_id_raw is not None:
                category_id = int(self._decode(category_id_raw))
                if category_id not in category_to_subcategories:
                    category_to_subcategories[category_id] = []
                category_to_subcategories[category_id].append(subcategory)

        if not category_to_subcategories:
            return

        categories: list[Category | None] = await self.get_categories(
            *category_to_subcategories.keys()
        )
        updated_categories: list[Category] = []

        for category in categories:
            if category is None:
                continue

            new_subcategories_map = {
                (subcategory.id, subcategory.type): subcategory
                for subcategory in category_to_subcategories[category.id]
            }
            new_subcategories_list: list[Subcategory] = [
                new_subcategories_map.get((old.id, old.type), old)
                for old in category.subcategories
            ]

            updated_categories.append(
                category.model_copy(update={'subcategories': tuple(new_subcategories_list)})
            )

        if updated_categories:
            await self.save_categories(*updated_categories)

    async def remove_subcategories(
        self, subcategory_type: SubcategoryType, *subcategory_ids: int
    ) -> None:
        subcategory_name: str = self._get_key(StoragePrefix.SUBCATEGORY)
        ids_to_remove: list[int] = [*subcategory_ids]

        if not subcategory_ids:
            all_of_type: list[Subcategory | None] = await self.get_subcategories(subcategory_type)
            ids_to_remove = [
                subcategory.id for subcategory in all_of_type if subcategory is not None
            ]

        if not ids_to_remove:
            return

        keys: list[str] = [
            self._get_subcategory_key(subcategory_type, subcategory_id)
            for subcategory_id in ids_to_remove
        ]
        category_ids_raw: list[str | bytes | None] = await self._redis.hmget(
            subcategory_name, keys
        )

        category_to_removals: dict[int, set[int]] = {}
        valid_keys_to_delete: list[str] = []

        for subcategory_id, category_id_raw, key in zip(ids_to_remove, category_ids_raw, keys):
            if category_id_raw is not None:
                category_id = int(self._decode(category_id_raw))
                if category_id not in category_to_removals:
                    category_to_removals[category_id] = set()
                category_to_removals[category_id].add(subcategory_id)
                valid_keys_to_delete.append(key)

        if not category_to_removals:
            return

        categories: list[Category | None] = await self.get_categories(*category_to_removals.keys())
        updated_categories: list[Category] = []

        for category in categories:
            if category is None:
                continue

            to_remove = category_to_removals[category.id]
            new_subcategories: list[Subcategory] = [
                subcategory
                for subcategory in category.subcategories
                if not (subcategory.id in to_remove and subcategory.type == subcategory_type)
            ]
            updated_categories.append(
                category.model_copy(update={'subcategories': tuple(new_subcategories)})
            )

        if updated_categories:
            await self.save_categories(*updated_categories)

        if valid_keys_to_delete:
            await self._redis.hdel(subcategory_name, *valid_keys_to_delete)

    async def mark_message_as_sent_by_bot(self, message_id: int, by_bot: bool = True) -> None:
        name: str = self._get_key(StoragePrefix.SENT_BY_BOT)

        if by_bot:
            await self._redis.sadd(name, str(message_id))
        else:
            await self._redis.srem(name, str(message_id))

    async def is_message_sent_by_bot(self, message_id: int) -> bool:
        name: str = self._get_key(StoragePrefix.SENT_BY_BOT)

        return bool(await self._redis.sismember(name, str(message_id)))
