# types/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## Submodules

- [`pages/`](pages/_MODULE_AUTO.md) (12 py, 12 cls)
- [`requests/`](requests/_MODULE_AUTO.md) (1 py, 10 cls)

## base.py
```
__all__ = ('FunPayObject', 'FunPayMutableObject')

cls FunPayObject(BindableObject, BaseModel)
  # Base class for all FunPay-parsed objects.

cls FunPayMutableObject(FunPayObject, BaseModel)

```

## calc.py
```
__all__ = ('CalcResult', 'MethodResult')

cls MethodResult(FunPayObject, BaseModel)
  # Represents a result of offer price calculation method (`lots/calc`) for a
  price_money_value() -> MoneyValue
  currency() -> Currency

cls CalcResult(FunPayObject, BaseModel)
  # Represents a result of offer price calculation method (`lots/calc`).

```

## categories.py
```
__all__ = ('Category', 'Subcategory')

cls Category(FunPayObject, BaseModel)
  # Represents a category from FunPay main page.
  full_name() -> str

cls Subcategory(FunPayObject, BaseModel)
  # Represents a subcategory from FunPay main page.

```

## chat.py
```
__all__ = ('PrivateChatPreview', 'Chat', 'PrivateChatInfo')

cls PrivateChatPreview(FunPayObject, BaseModel)
  # Represents a private chat preview.

cls Chat(FunPayObject, BaseModel)
  # Represents a chat.

cls PrivateChatInfo(FunPayObject, BaseModel)
  # Represents a private chat info.
  registration_timestamp() -> int
    # Interlocutors registration timestamp.

```

## common.py
```
__all__ = …

cls MoneyValue(FunPayObject, BaseModel)
  # Represents a monetary value with an associated currency.
  currency() -> Currency

cls UserBadge(FunPayObject, BaseModel)
  # Represents a user badge.
  type() -> BadgeType
    # Badge type.

cls UserPreview(FunPayObject, BaseModel)
  # Represents user preview.

cls UserRating(FunPayObject, BaseModel)
  # Represents full user rating.

cls Achievement(FunPayObject, BaseModel)
  # Represents a user achievement.

cls CurrentlyViewingOfferInfo(FunPayObject, BaseModel)
  # represents a currently viewing offer info.

cls RaiseOffersResponse(FunPayObject, BaseModel)
  # Represents a response to lot raise request.
  unlock_at_datetime() -> datetime
    # Datetime object of the time when the next raise is available.

cls PaymentOption(FunPayObject)
  # Represents an offer payment option (typically from offer page).

cls DetailedUserBalance(FunPayObject)
  # Represents a detailed user balance (typically from offer page).

```

## common_page_elements.py
```
__all__ = ('AppData', 'WebPush', 'PageHeader')

cls WebPush(FunPayObject, BaseModel)
  # Represents a WebPush data extracted from an AppData dict.

cls AppData(FunPayObject, BaseModel)
  # Represents an AppData dict.

cls PageHeader(FunPayObject, BaseModel)
  # Represents the header section of a FunPay page.

```

## enums.py
```
cls TransactionFilter(str, Enum): ALL, PAYMENT, WITHDRAW, ORDER, OTHER
  # Transaction list filter values for ``users/transactions``.

cls OrderPreviewType(Enum): SALE, PURCHASE, UNKNOWN

cls NoticeChannel(Enum): EMAIL, PUSH, TELEGRAM

```

## finances.py
```
__all__ = ('TransactionPreview', 'TransactionInfo', 'TransactionPreviewsBatch')

cls TransactionPreview(FunPayObject, BaseModel)
  # Represents a transaction preview.
  timestamp() -> int
    # Transaction timestamp.

cls TransactionInfo(FunPayObject, BaseModel)
  # Represents a transaction info.

cls TransactionPreviewsBatch(FunPayObject, BaseModel)
  # Represents a single batch of transaction previews returned by FunPay.
  async next_batch() -> TransactionPreviewsBatch

```

## messages.py
```
__all__ = ('Message',)

cls MessageMeta(FunPayObject, BaseModel)
  # Represents a message meta info.

cls Message(FunPayObject, BaseModel)
  # Represents a message from any FunPay chat (private or public).
  chat_identifier() -> int | str | None
  from_me() -> bool
  timestamp() -> int
  async reply(text: str? = None, image: str | BytesIO | int? = None, enforce_whitespaces: bool = True, keep_chat_unread: Literal[False] = False) -> Message
  async reply(text: str? = None, image: str | BytesIO | int? = None, enforce_whitespaces: bool = True, keep_chat_unread: Literal[True] = True) -> None
  async reply(text: str? = None, image: str | BytesIO | int? = None, enforce_whitespaces: bool = True, keep_chat_unread: Literal[True] | Literal[False] = False) -> Message | None
  async chat(update: bool = False) -> Chat
  async chat_page(update: bool = False) -> ChatPage
  async sender_profile_page(update: bool = False) -> ProfilePage
  async is_sent_by_bot() -> bool
  async mark_as_sent_by_bot(bot: Bot? = None, by_bot: bool = True) -> None

```

## offers.py
```
__all__ = ('OfferPreview', 'OfferSeller', 'OfferFields')
T = TypeVar('T')
P = ParamSpec('P')

cls OfferSeller(FunPayObject, BaseModel)
  # Represents the seller of an offer.
  registration_timestamp() -> int
    # The seller's registration timestamp.

cls OfferPreview(FunPayObject, BaseModel)
  # Represents an offer preview.

cls OfferFields(FunPayMutableObject, BaseModel)
  # Represents the full set of form fields used to construct or update
  set_field(key: str, value: Any) -> None
    # Manually set or remove a raw field value.
  convert_to_currency(category_id: int, subcategory_id: int) -> Self
    # Transform this `OfferFields` instance into a **currency offer** configuration.
  convert_to_common(subcategory_id: int?, offer_id: int) -> Self
    # Transform this `OfferFields` instance into a **common offer** configuration.
  get_currency_amount(server_id: int, side_id: int) -> float | None
    # Gets the currency amount.
  set_currency_amount(server_id: int, side_id: int, amount: int | float?) -> None
    # Sets the currency amount.
  get_currency_price(server_id: int, side_id: int) -> float | None
    # Gets the currency price.
  set_currency_price(server_id: int, side_id: int, price: int | float?) -> None
    # Sets the currency price.
  get_currency_status(server_id: int, side_id: int) -> bool | None
    # Gets the currency active status.
  set_currency_status(server_id: int, side_id: int, status: bool?) -> None
    # Sets the currency active status.
  is_currency() -> bool
    # Whether this ``OfferFields`` instance is a currency-type or not.
  is_common() -> bool
    # Whether this ``OfferFields`` instance is a common-type or not.
  subcategory_id() -> int | None
    # Subcategory ID.
  subcategory_id(value: int?) -> None
  category_id() -> int | None
    # Category ID.
  category_id(value: int?) -> None
  min_sum() -> float | None
    # Minimum order sum.
  min_sum(value: float | int?) -> None
    # Offer title (Russian).
  offer_id() -> int | None
    # Offer ID.
  offer_id(offer_id: int?) -> None
  title_ru() -> str | None
    # Offer title (Russian).
  title_ru(value: str?) -> None
  title_en() -> str | None
    # Offer title (English).
  title_en(value: str?) -> None
  desc_ru() -> str | None
    # Offer description (Russian).
  desc_ru(value: str?) -> None
  desc_en() -> str | None
    # Offer description (English).
  desc_en(value: str?) -> None
  payment_msg_ru() -> str | None
    # Payment message (Russian).
  payment_msg_ru(value: str?) -> None
  payment_msg_en() -> str | None
    # Payment message (English).
  payment_msg_en(value: str?) -> None
  images() -> list[int] | None
    # List of image IDs.
  images(value: list[int]?) -> None
  secrets() -> list[str] | None
    # List of goods in auto delivery.
  secrets(value: list[str]?) -> None
  active() -> bool
    # Whether the offer is active or not.
  active(value: bool?) -> None
  auto_delivery() -> bool
    # Whether the auto_delivery is enabled for this offer or not.
  auto_delivery(value: bool?) -> None
  deactivate_after_sale() -> bool
    # Whether the deactivation after sale is enabled for this offer or not.
  deactivate_after_sale(value: bool?) -> None
  price() -> float | None
    # Offer price.
  price(value: float) -> None
  amount() -> int | None
    # Goods amount.
  amount(value: int?) -> None

chips_only(func: Callable[P, T]) -> Callable[P, T]

common_only(func: Callable[P, T]) -> Callable[P, T]

```

## orders.py
```
__all__ = ('OrderPreview', 'OrderPreviewsBatch')

cls OrderPreview(FunPayObject, BaseModel)
  # Represents an order preview.
  model_post_init(context: dict[Any, Any]) -> None
  timestamp() -> int
    # Order timestamp.

cls OrderPreviewsBatch(FunPayObject)
  # Represents a single batch of order previews.
  model_post_init(context: dict[Any, Any]) -> None
  async next_batch() -> OrderPreviewsBatch
  order_id_filter() -> str | None
  buyer_username_filter() -> str | None
  status_filter() -> OrderStatus | str | None
  game_id_filter() -> int | None
  other_filters() -> dict[str, str] | None
  type() -> OrderPreviewType

```

## reviews.py
```
__all__ = ('Review', 'ReviewsBatch')

cls Review(FunPayObject, BaseModel)
  # Represents a review.
  timestamp() -> int
    # Review timestamp.

cls ReviewsBatch(FunPayObject, BaseModel)
  # Represents a single batch of reviews.

```

## settings.py
```
__all__ = ('Settings',)

cls Settings(FunPayObject)
  # Represents user settings (``https://funpay.com/account/settings``).

```

## sras.py
```
__all__ = ('SrasSectionRestriction',)

cls SrasSectionRestriction(FunPayObject)
  # Represents a SRAS restriction for a specific subcategory.

```

## updates.py
```
__all__ = …
UpdateData = TypeVar('UpdateData')

cls OrdersCounters(FunPayObject, BaseModel)
  # Represents an order counters data from runner response.

cls ChatBookmarks(FunPayObject, BaseModel)
  # Represents a chat bookmarks data from runner response.

cls ChatCounter(FunPayObject, BaseModel)
  # Represents a chat counter data from runner response.

cls NodeInfo(FunPayObject, BaseModel)
  # Represents a chat info in chat data from runner response.

cls ChatNode(FunPayObject, BaseModel)
  # Represents a chat data from runner response.

cls ActionResponse(FunPayObject, BaseModel)
  # Represents an action response data from runner response.

cls RunnerResponseObject(FunPayObject, BaseModel, Generic[UpdateData])
  # Represents a single runner response object from runner response.

cls RunnerResponse(FunPayObject, BaseModel)
  # Represents a runner response.
  convert_to_immutable(value: Any) -> tuple[MappingProxyType[str, Any], ...] | None
  get_timestamp(value: Any, info: ValidationInfo) -> int

```
