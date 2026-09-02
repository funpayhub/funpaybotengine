# client/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## Submodules

- [`session/`](session/_MODULE_AUTO.md) (3 py, 5 cls)

## bot.py
```
__all__ = ('Bot',)
F = TypeVar('F', bound=Callable[..., Any])
R = TypeVar('R', bound=Any)

cls LocaleMismatchHookProto(Protocol)

cls Bot
  __init__(golden_key: str = '', session: BaseSession? = None, storage: Storage? = None, *, phpsessid: str? = None, proxy: str? = None, default_headers: dict[str, Any]? = None, update_categories: bool = True) -> None
  anonymous() -> bool
    # Whether this bot instance is anonymous or not.
  initialized() -> bool
    # Whether this bot instance is initialized or not.
  golden_key() -> str
    # Golden key (token).
  golden_seal() -> str | None
  csrf_token() -> str
    # CSRF token. Available only after initialization (``Bot.update`` method).
  phpsessid() -> str
    # PHPSESSID. Available only after initialization (``Bot.update`` method).
  logout_token() -> str
    # Logout token. Available only after initialization (``Bot.update`` method).
  userid() -> int
  username() -> str | None
  locale() -> Language
    # Bot locale. Available only after initialization (``Bot.update`` method).
  currency() -> Currency
    # Bot currency. Available only after initialization (``Bot.update`` method).
  session() -> BaseSession
    # Bot session.
  storage() -> Storage
  session_updated_at() -> int
  set_on_locale_mismatch_hook(hook: LocaleMismatchHookProto) -> None
  async runner_request(objects_to_request: Sequence[RequestableObject] | Literal[False] = False, action: Action | Literal[False] = False) -> RunnerResponse
    # Makes request to the runner.
  async mute_chat(chat_id: int, mute: bool) -> bool
  async raise_offers(category_id: int, *subcategory_ids: int) -> RaiseOffersResponse
  async upload_chat_image(file: str | BytesIO) -> int
    # Uploads an image to FunPay servers for use in chat messages.
  async upload_avatar(file: str | BytesIO) -> bool
  async send_message(chat_id: int | str, text: str? = None, image: str | BytesIO | int? = None, enforce_whitespaces: bool = True, keep_chat_unread: Literal[False] = False) -> Message
  async send_message(chat_id: int | str, text: str? = None, image: str | BytesIO | int? = None, enforce_whitespaces: bool = True, keep_chat_unread: Literal[True] = True) -> None
  async send_message(chat_id: int | str, text: str? = None, image: str | BytesIO | int? = None, enforce_whitespaces: bool = True, keep_chat_unread: bool = False) -> Message | None
    # Send a message to a chat.
  async refund(order_id: str) -> bool
  async review(order_id: str, text: str, rating: Literal[0, 1, 2, 3, 4, 5]) -> bool
  async delete_review(order_id: str) -> bool
  async save_offer_fields(offer_fields: OfferFields) -> bool
  async calc_chips(game_id: int, price: float) -> CalcResult
  async calc_lots(subcategory_id: int, price: float) -> CalcResult
  async logout() -> bool
  async set_notification_status(enabled: bool, channel: NoticeChannel) -> bool
  async set_telegram_notification_status(enabled: bool) -> bool
  async set_push_notification_status(enabled: bool) -> bool
  async set_email_notification_status(enabled: bool) -> bool
  async set_offers_hidden(hidden: bool) -> bool
  async get_currently_viewing_offer(*user_ids: int, user_id: None = None) -> dict[int, CurrentlyViewingOfferInfo | bool]
  async get_currently_viewing_offer(*, user_id: int) -> CurrentlyViewingOfferInfo | bool
  async get_currently_viewing_offer(*user_ids: int, user_id: int? = None) -> dict[int, CurrentlyViewingOfferInfo | bool] | CurrentlyViewingOfferInfo | bool
    # Returns the last offer that the user has seen recently
  async get_unread_chats_amount() -> int
    # Returns the amount of unread chats
  async get_active_orders_amount() -> tuple[int, int]
    # Returns the amount of active orders (purchases, sales)
  async get_recent_chat_previews() -> list[PrivateChatPreview]
    # Returns the list of recent chat previews
  async get_chat_messages(*, chat_id: int | str, after_message_id: int? = None) -> list[Message]
  async get_chat_messages(*args: tuple[int | str, int?], chat_id: None = None, after_message_id: None = None) -> dict[int, list[Message]]
  async get_chat_messages(*args: tuple[int | str, int?], chat_id: int | str? = None, after_message_id: int? = None) -> list[Message] | dict[int, list[Message]]
    # Retrieves the 100 most recent messages in a chat,
  async get_telegram_connect_url() -> str
  async get_chat_history(chat_id: int | str, before_message_id: int = 999999999999999999) -> list[Message]
    # Retrieves the 100 most recent messages in a chat,
  async get_sales(from_order_id: str? = None, order_id_filter: str? = None, buyer_username_filter: str? = None, status_filter: OrderStatus | str? = None, game_id_filter: int? = None, other_filters: dict[str, str]? = None) -> OrderPreviewsBatch
    # Fetch the latest 100 sales, optionally filtered by various criteria.
  async get_purchases(from_order_id: str? = None, order_id_filter: str? = None, seller_username_filter: str? = None, status_filter: OrderStatus | str? = None, game_id_filter: int? = None, other_filters: dict[str, str]? = None) -> OrderPreviewsBatch
    # Fetch the latest 100 purchases, optionally filtered by various criteria.
  async get_offer_fields(subcategory_type: SubcategoryType = ..., subcategory_id: int = ..., subcategory: None = ..., offer_id: None = ...) -> OfferFields
  async get_offer_fields(subcategory_type: None = ..., subcategory_id: None = ..., subcategory: Subcategory = ..., offer_id: None = ...) -> OfferFields
  async get_offer_fields(subcategory_type: None = ..., subcategory_id: None = ..., subcategory: None = ..., offer_id: int = ...) -> OfferFields
  async get_offer_fields(subcategory_type: SubcategoryType? = None, subcategory_id: int? = None, subcategory: Subcategory? = None, offer_id: int? = None) -> OfferFields
  async get_transactions(from_transaction_id: int = 0, filter: TransactionFilter | str = ...) -> TransactionPreviewsBatch
  async get_main_page() -> MainPage
    # Retrieves the FunPay main page.
  async get_chat_page(chat_id: int | str) -> ChatPage
    # Retrieves the chat page.
  async get_profile_page(id: int) -> ProfilePage
  async get_subcategory_page(subcategory_type: SubcategoryType, subcategory_id: int) -> SubcategoryPage
  async get_offer_page(offer_id: int | str) -> OfferPage
  async get_my_offers_page(subcategory_id: int) -> MyOffersPage
  async get_my_chips_page(subcategory_id: int) -> MyChipsPage
  async get_order_page(order_id: str) -> OrderPage
  async get_sras_info_page() -> SrasInfoPage
    # Retrieves the SRAS info page with seller rating restrictions per subcategory.
  async get_settings_page() -> SettingsPage
  async get_transactions_page() -> TransactionsPage
  async get_settings() -> Settings
  async get_2fa_status() -> bool
  async check_banned() -> bool
  async make_request(method: FunPayMethod[MethodReturnType], skip_update: bool = False, skip_locale_check: bool = False, skip_session_cookies: bool = False) -> Response[MethodReturnType]
  async update(change_locale: Language? = None) -> Self
  async listen_events(*, config: RunnerConfig? = None, session_storage: Storage? = None, workflow_injection: dict[str, Any]? = None) -> None
  async stop_listening() -> None

```

## default_hooks.py
```
R = TypeVar('R', bound=Any)

async force_locale_hook(method: FunPayMethod[R], bot: Bot, response: Response[R]) -> Response[R]

async ignore_locale_hook(method: FunPayMethod[R], bot: Bot, response: Response[R]) -> Response[R]

```
