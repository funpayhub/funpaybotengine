# methods/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## base.py
```
__all__ = ('FunPayMethod', 'MethodReturnType')
R = TypeVar('R')
MethodReturnType = TypeVar('MethodReturnType', bound=Any)

cls FunPayMethod(BaseModel, Generic[MethodReturnType], ABC)
  # Base method class.
  model_post_init() -> None
  async parse_result(response: RawResponse[Any]) -> Any
    # Method that parses raw response.
  async transform_result(parsing_result: Any, response: RawResponse[Any]) -> MethodReturnType
    # Transforms a raw response or parser output
  async to_obj(response: RawResponse[Any]) -> MethodReturnType
  async get_full_context(response: RawResponse[Any], context: dict[str, Any]? = None) -> dict[str, Any]
  async get_url(bot: Bot) -> str
  async get_headers(bot: Bot) -> dict[str, str]
  async get_data(bot: Bot) -> dict[str, Any]
  async get_context(bot: Bot) -> dict[str, Any]
  async execute(as_: Bot) -> Response[MethodReturnType]
    # Execute method as bot and return result.

```

## calc_chips.py
```
__all__ = ('CalcChips',)

cls CalcChips(FunPayMethod[CalcResult], BaseModel)
  __init__(game_id: int, price: float) -> None
  async parse_result(response: RawResponse[CalcResult]) -> dict[str, Any]

```

## calc_lots.py
```
__all__ = ('CalcLots',)

cls CalcLots(FunPayMethod[CalcResult], BaseModel)
  __init__(subcategory_id: int, price: float) -> None
  async parse_result(response: RawResponse[CalcResult]) -> dict[str, Any]

```

## check_banned.py
```
__all__ = ('CheckBanned',)

cls CheckBanned(FunPayMethod[bool], BaseModel)
  __init__() -> None
  async parse_result(response: RawResponse[bool]) -> bool
  async transform_result(parsing_result: bool, response: RawResponse[bool]) -> bool
  async execute(as_: Bot) -> Response[bool]

```

## delete_review.py
```
__all__ = ('DeleteReview',)

cls DeleteReview(FunPayMethod[bool], BaseModel)
  # Delete a review / reply to review (``https://funpay.com/orders/reviewDelete``).
  __init__(order_id: str, locale: Language? = None)
  async parse_result(response: RawResponse[Any]) -> bool
  async transform_result(parsing_result: Any, response: RawResponse[Any]) -> bool

async make_data(method: DeleteReview, bot: Bot) -> dict[str, Any]

```

## get_2fa_status.py
```
__all__ = ('Get2faStatus',)

cls Get2faStatus(FunPayMethod[bool])
  __init__() -> None
  async parse_result(response: RawResponse[bool]) -> bool
  async transform_result(parsing_result: bool, response: RawResponse[bool]) -> bool

```

## get_chat_history.py
```
__all__ = ('GetChatHistory',)

cls GetChatHistory(FunPayMethod[list[Message]], BaseModel)
  # Get chat history method (``https://funpay.com/chat/history``).
  __init__(chat_id: int | str, before_message_id: int = 999999999999999999, locale: Language? = None)
    # :param chat_id: Chat ID.
  async parse_result(response: RawResponse[Any]) -> list[ParserMessage]
  async transform_result(parsing_result: list[ParserMessage], response: RawResponse[Any]) -> list[Message]

```

## get_chat_page.py
```
__all__ = ('GetChatPage',)

cls GetChatPage(FunPayMethod[ChatPage], BaseModel)
  # Get chat method (``https://funpay.com/chat/history``).
  __init__(chat_id: int | str, locale: Language? = None)
    # :param chat_id: Chat ID.

```

## get_main_page.py
```
__all__ = ('GetMainPage',)

cls GetMainPage(FunPayMethod[MainPage], BaseModel)
  # Get the main page method (``https://funpay.com/``).
  __init__(locale: Language? = None, change_locale: Language? = None)

```

## get_my_chips_page.py
```
__all__ = ('GetMyChipsPage',)

cls GetMyChipsPage(FunPayMethod[MyChipsPage])
  # Get personal chips page (``https://funpay.com/chips/<subcategory_id>/trade``).
  __init__(subcategory_id: int)

```

## get_my_offers_page.py
```
__all__ = ('GetMyOffersPage',)

cls GetMyOffersPage(FunPayMethod[MyOffersPage])
  # Get personal lots page (``https://funpay.com/lots/<subcategory_id>/trade``).
  __init__(subcategory_id: int)

```

## get_offer_fields.py
```
__all__ = ('GetOfferFields',)

cls GetOfferFields(FunPayMethod[OfferFields], BaseModel)
  # Get offer fields method.
  __init__(subcategory_type: SubcategoryType, subcategory_id: int, offer_id: int? = None, locale: Language? = None)

```

## get_offer_page.py
```
__all__ = ('GetOfferPage',)

cls GetOfferPage(FunPayMethod[OfferPage], BaseModel)
  # Get an order page method (``https://funpay.com/<lots/chips>/offer?id=<offer_id>``).
  __init__(offer_id: int | str, locale: Language? = None)

```

## get_order_page.py
```
__all__ = ('GetOrderPage',)

cls GetOrderPage(FunPayMethod[OrderPage], BaseModel)
  # Get an order page method (``https://funpay.com/orders/<order_id>/``).
  __init__(order_id: str, locale: Language? = None)

```

## get_profile_page.py
```
__all__ = ('GetProfilePage',)

cls GetProfilePage(FunPayMethod[ProfilePage], BaseModel)
  # Get a profile page method (``https://funpay.com/users/<user_id>/``).
  __init__(user_id: int, locale: Language? = None)

```

## get_purchases.py
```
__all__ = ('GetPurchases',)
STATE_FILTERS = {OrderStatus.COMPLETED: 'closed', OrderStatus.PAID: 'paid', OrderStatus.REFUNDED: 'refunded'}

cls GetPurchases(FunPayMethod[OrderPreviewsBatch], BaseModel)
  # Get a purchases list (``https://funpay.com/orders/``).
  __init__(from_order_id: str? = None, order_id_filter: str? = None, seller_username_filter: str? = None, status_filter: OrderStatus | str? = None, game_id_filter: int? = None, other_filters: dict[str, str]? = None, locale: Language? = None)

```

## get_reviews.py
```
__all__ = ('GetReviews',)
STATE_FILTERS = {OrderStatus.COMPLETED: 'closed', OrderStatus.PAID: 'paid', OrderStatus.REFUNDED: 'refunded'}

cls GetReviews(FunPayMethod[ReviewsBatch], BaseModel)
  # Get a sales list (``https://funpay.com/orders/trade``).
  __init__(user_id: int, from_review_id: str = '', filter: str = '', locale: Language? = None)

```

## get_sales.py
```
__all__ = ('GetSales',)
STATE_FILTERS = {OrderStatus.COMPLETED: 'closed', OrderStatus.PAID: 'paid', OrderStatus.REFUNDED: 'refunded'}

cls GetSales(FunPayMethod[OrderPreviewsBatch], BaseModel)
  # Get a sales list (``https://funpay.com/orders/trade``).
  __init__(from_order_id: str? = None, order_id_filter: str? = None, buyer_username_filter: str? = None, status_filter: OrderStatus | str? = None, game_id_filter: int? = None, other_filters: dict[str, str]? = None, locale: Language? = None)

```

## get_settings_page.py
```
__all__ = ('GetSettingPage',)

cls GetSettingPage(FunPayMethod[SettingsPage])
  # Get user settings page (``https://funpay.com/account/settings``).
  __init__() -> None

```

## get_sras_info_page.py
```
__all__ = ('GetSrasInfoPage',)

cls GetSrasInfoPage(FunPayMethod[SrasInfoPage])
  # Get SRAS info page (``https://funpay.com/sras/info``).
  __init__() -> None

```

## get_subcategory_page.py
```
__all__ = ('GetSubcategoryPage',)

cls GetSubcategoryPage(FunPayMethod[SubcategoryPage], BaseModel)
  # Get a subcategory page method (``https://funpay.com/<lots/chips>/<subcategory_id>/``).
  __init__(type: SubcategoryType, subcategory_id: int, locale: Language? = None)

```

## get_telegram_connect_url.py
```
__all__ = ('GetTelegramConnectURL',)

cls GetTelegramConnectURL(FunPayMethod[str])
  # Get telegram connect url via @funpaysmartbot (``https://funpay.com/account/linkTelegram``).
  __init__() -> None
  async parse_result(response: RawResponse[Any]) -> str
  async transform_result(parsing_result: str, response: RawResponse[Any]) -> str

```

## get_transactions.py
```
__all__ = ('GetTransactions',)

cls GetTransactions(FunPayMethod[TransactionPreviewsBatch], BaseModel)
  # Get the main page method (``https://funpay.com/``).
  __init__(filter: TransactionFilter | str = ..., from_transaction_id: int? = None, locale: Language? = None)

async make_data(method: GetTransactions, bot: Bot) -> dict[str, Any]

```

## get_transactions_page.py
```
__all__ = ('GetTransactionsPage',)

cls GetTransactionsPage(FunPayMethod[TransactionsPage], BaseModel)
  # Get the transactions page (``https://funpay.com/account/balance``).
  __init__(locale: Language? = None)

```

## logout.py
```
__all__ = ('Logout',)

cls Logout(FunPayMethod[bool])
  # Logout from current account (``https://funpay.com/account/logout``).
  __init__(logout_token: str)
  async parse_result(response: RawResponse[Any]) -> bool
  async transform_result(parsing_result: bool, response: RawResponse[Any]) -> bool

```

## mute_chat.py
```
__all__ = ('MuteChat',)

cls MuteChat(FunPayMethod[bool])
  __init__(chat_id: int, mute: bool) -> None
  async parse_result(response: RawResponse[bool]) -> bool
  async transform_result(parsing_result: Any, response: RawResponse[bool]) -> bool

```

## raise_offers.py
```
__all__ = ('RaiseOffers',)

cls RaiseOffers(FunPayMethod[RaiseOffersResponse])
  __init__(category_id: int, subcategory_ids: Sequence[int], locale: Language? = None)
  async parse_result(response: RawResponse[bool]) -> dict[str, Any]

```

## refund.py
```
__all__ = ('Refund',)

cls Refund(FunPayMethod[bool], BaseModel)
  # Refund an order (``https://funpay.com/orders/refund``).
  __init__(order_id: str, locale: Language? = None)
  async parse_result(response: RawResponse[Any]) -> bool
  async transform_result(parsing_result: Any, response: RawResponse[Any]) -> bool

```

## review.py
```
__all__ = ('Review',)

cls Review(FunPayMethod[bool], BaseModel)
  # Leave / Edit a review / reply to review (``https://funpay.com/orders/review``).
  __init__(order_id: str, text: str, rating: Literal[0, 1, 2, 3, 4, 5], locale: Language? = None)
  async parse_result(response: RawResponse[Any]) -> bool
  async transform_result(parsing_result: Any, response: RawResponse[Any]) -> bool

async make_data(method: Review, bot: Bot) -> dict[str, Any]

```

## runner_request.py
```
__all__ = ('RunnerRequest',)

cls RunnerRequest(FunPayMethod[RunnerResponse], BaseModel)
  # Get info from runner (``https://funpay.com/runner``).
  __init__(objects_to_request: Sequence[RequestableObject] | Literal[False] = False, action: Action | Literal[False] = False, locale: Language? = None)
  async transform_result(parsing_result: PRunnerResponse, response: RawResponse[Any]) -> RunnerResponse

async make_data(method: RunnerRequest, bot: Bot) -> dict[str, str]

```

## save_offer_fields.py
```
__all__ = ('SaveOfferFields',)

cls SaveOfferFields(FunPayMethod[bool], BaseModel)
  # Get offer fields method.
  __init__(offer_fields: OfferFields, locale: Language? = None)
  async parse_result(response: RawResponse[Any]) -> bool | dict[str, Any]
  async transform_result(parsing_result: bool | dict[str, Any], response: RawResponse[Any]) -> bool

```

## set_offers_hidden.py
```
__all__ = ('SetOffersHidden',)

cls SetOffersHidden(FunPayMethod[bool])
  # Update offers hidden status (``https://funpay.com/trade/tradeLockSettings``).
  __init__(hidden: bool)
  async parse_result(response: RawResponse[Any]) -> bool
  async transform_result(parsing_result: Any, response: RawResponse[Any]) -> bool

async make_data(method: SetOffersHidden, bot: Bot) -> dict[str, Any]

```

## update_notice_channel.py
```
__all__ = ('UpdateNoticeChannel',)

cls UpdateNoticeChannel(FunPayMethod[bool])
  # Update notification channel status (``https://funpay.com/account/noticeChannel``).
  __init__(channel: NoticeChannel, enabled: bool)
  async parse_result(response: RawResponse[Any]) -> bool
  async transform_result(parsing_result: Any, response: RawResponse[Any]) -> bool

```

## upload_avatar.py
```
__all__ = ('UploadAvatar',)

cls UploadAvatar(FunPayMethod[bool], BaseModel)
  # Uploads new user avatar (``https://funpay.com/avatar``).
  __init__(file: str | BytesIO)
  async transform_result(parsing_result: str, response: RawResponse[Any]) -> bool

```

## upload_image.py
```
__all__ = ('UploadImage',)

cls UploadImage(FunPayMethod[int], BaseModel)
  # Uploads chat image (``https://funpay.com/``).
  __init__(file: str | BytesIO, locale: Language? = None)
  async transform_result(parsing_result: str, response: RawResponse[Any]) -> int

```
