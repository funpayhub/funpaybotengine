# storage/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## base.py
```
__all__ = ('Storage',)

cls Storage(ABC)
  async get_chat_preview(chat_id: int) -> PrivateChatPreview | None
    # Retrieve a single chat preview.
  async get_chat_previews(*chat_ids: int) -> list[PrivateChatPreview | None]
    # Retrieve multiple chat previews.
  async save_chat_previews(*chats: PrivateChatPreview) -> None
    # Save provided chat previews.
  async remove_chat_previews(*chat_ids: int) -> None
    # Removes chat previews with provided chat IDs. If no chat IDs are provided,
  async get_order_preview(order_id: str) -> OrderPreview | None
    # Retrieve a single order preview.
  async get_order_previews(*order_ids: str) -> list[OrderPreview | None]
    # Retrieve multiple order previews.
  async save_order_previews(*orders: OrderPreview) -> None
    # Save provided order previews.
  async remove_order_previews(*order_ids: str) -> None
    # Removes order previews with provided order IDs. If no order IDs are provided,
  async get_category(category_id: int) -> Category | None
    # Retrieve a single category.
  async get_categories(*category_ids: int) -> list[Category | None]
    # Retrieve multiple categories.
  async save_categories(*categories: Category) -> None
    # Save provided categories.
  async remove_categories(*category_ids: int) -> None
    # Removes categories with provided category IDs. If no category IDs are provided,
  async get_subcategory(subcategory_type: SubcategoryType, subcategory_id: int) -> Subcategory | None
    # Retrieve a single subcategory.
  async get_subcategories(subcategory_type: SubcategoryType, *subcategory_ids: int) -> list[Subcategory | None]
    # Retrieve multiple subcategories.
  async save_subcategories(*subcategories: Subcategory) -> None
    # Save the provided subcategories.
  async remove_subcategories(subcategory_type: SubcategoryType, *subcategory_ids: int) -> None
    # Removes subcategories with provided subcategory type and subcategory IDs.
  async mark_message_as_sent_by_bot(message_id: int, by_bot: bool = True) -> None
    # Mark a message as sent by the bot.
  async is_message_sent_by_bot(message_id: int) -> bool
    # Check whether a message was sent by the bot.

```

## inmemory.py
```
__all__ = ('InMemoryStorage',)

cls InMemoryStorage(Storage)
  __init__() -> None
  async get_chat_preview(chat_id: int) -> PrivateChatPreview | None
  async get_chat_previews(*chat_ids: int) -> list[PrivateChatPreview | None]
  async save_chat_previews(*chats: PrivateChatPreview) -> None
  async remove_chat_previews(*chat_ids: int) -> None
  async get_order_preview(order_id: str) -> OrderPreview | None
  async get_order_previews(*order_ids: str) -> list[OrderPreview | None]
  async save_order_previews(*orders: OrderPreview) -> None
  async remove_order_previews(*order_ids: str) -> None
  async get_category(category_id: int) -> Category | None
  async get_categories(*category_ids: int) -> list[Category | None]
  async save_categories(*categories: Category) -> None
  async remove_categories(*category_ids: int) -> None
  async get_subcategory(subcategory_type: SubcategoryType, subcategory_id: int) -> Subcategory | None
  async get_subcategories(subcategory_type: SubcategoryType, *subcategory_ids: int) -> list[Subcategory | None]
  async save_subcategories(*subcategories: Subcategory) -> None
  async remove_subcategories(subcategory_type: SubcategoryType, *subcategory_ids: int) -> None
  async mark_message_as_sent_by_bot(message_id: int, by_bot: bool = True) -> None
  async is_message_sent_by_bot(message_id: int) -> bool

```

## redis.py
```
__all__ = ('RedisStorage',)
T = TypeVar('T', bound=FunPayObject)

cls StoragePrefix(str, Enum): CHAT, ORDER, CATEGORY, SUBCATEGORY, SENT_BY_BOT

cls RedisStorage(Storage)
  __init__(redis: Redis, key: str? = None) -> None
  async get_chat_preview(chat_id: int) -> PrivateChatPreview | None
  async get_chat_previews(*chat_ids: int) -> list[PrivateChatPreview | None]
  async save_chat_previews(*chats: PrivateChatPreview) -> None
  async remove_chat_previews(*chat_ids: int) -> None
  async get_order_preview(order_id: str) -> OrderPreview | None
  async get_order_previews(*order_ids: str) -> list[OrderPreview | None]
  async save_order_previews(*orders: OrderPreview) -> None
  async remove_order_previews(*order_ids: str) -> None
  async get_category(category_id: int) -> Category | None
  async get_categories(*category_ids: int) -> list[Category | None]
  async save_categories(*categories: Category) -> None
  async remove_categories(*category_ids: int) -> None
  async get_subcategory(subcategory_type: SubcategoryType, subcategory_id: int) -> Subcategory | None
  async get_subcategories(subcategory_type: SubcategoryType, *subcategory_ids: int) -> list[Subcategory | None]
  async save_subcategories(*subcategories: Subcategory) -> None
  async remove_subcategories(subcategory_type: SubcategoryType, *subcategory_ids: int) -> None
  async mark_message_as_sent_by_bot(message_id: int, by_bot: bool = True) -> None
  async is_message_sent_by_bot(message_id: int) -> bool

```
