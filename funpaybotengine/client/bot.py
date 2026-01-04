from __future__ import annotations


__all__ = ('Bot',)

import time
import asyncio
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Protocol, overload
from io import BytesIO
from asyncio import Lock, Event
from contextlib import suppress
from collections.abc import Callable, Sequence

from typing_extensions import Self

from funpaybotengine.types import (
    Message,
    Currency,
    Language,
    Settings,
    CalcResult,
    OfferFields,
    Subcategory,
    RunnerResponse,
    OrderPreviewsBatch,
    PrivateChatPreview,
    TransactionPreviewsBatch,
    CurrentlyViewingOfferInfo,
)
from funpaybotengine.utils import (
    random_runner_tag,
    check_message_text,
    enforce_message_text_whitespaces,
)
from funpaybotengine.runner import Runner
from funpaybotengine.methods import (
    Logout,
    Refund,
    Review,
    CalcLots,
    GetSales,
    MuteChat,
    CalcChips,
    CheckBanned,
    GetChatPage,
    GetMainPage,
    RaiseOffers,
    UploadImage,
    DeleteReview,
    FunPayMethod,
    Get2faStatus,
    GetOrderPage,
    GetPurchases,
    UploadAvatar,
    RunnerRequest,
    GetChatHistory,
    GetMyChipsPage,
    GetOfferFields,
    GetProfilePage,
    GetSettingPage,
    GetMyOffersPage,
    GetTransactions,
    SaveOfferFields,
    SetOffersHidden,
    MethodReturnType,
    GetSubcategoryPage,
    GetTransactionsPage,
    UpdateNoticeChannel,
    GetTelegramConnectURL,
)
from funpaybotengine.exceptions import (
    UserBannedError,
    BotUnauthenticatedError,
)
from funpaybotengine.types.enums import OrderStatus, NoticeChannel, SubcategoryType
from funpaybotengine.types.pages import (
    ChatPage,
    MainPage,
    OrderPage,
    FunPayPage,
    MyChipsPage,
    ProfilePage,
    MyOffersPage,
    SettingsPage,
    SubcategoryPage,
    TransactionsPage,
)
from funpaybotengine.storage.base import Storage
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.types.requests import (
    Action,
    RequestNodeInfo,
    CPURequestObject,
    NodeRequestObject,
    RequestableObject,
    SendMessageAction,
    SendingMessageData,
    ChatCounterRequestObject,
    ChatBookmarksRequestObject,
    OrdersCountersRequestObject,
)
from funpaybotengine.client.session.base import Response
from funpaybotengine.client.default_hooks import force_locale_hook
from funpaybotengine.storage.inmemory_storage import InMemoryStorage
from funpaybotengine.client.session.aiohttp_session import AioHttpSession


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import BaseSession
    from funpaybotengine.dispatching.routers.dispatcher import Dispatcher


F = TypeVar('F', bound=Callable[..., Any])
R = TypeVar('R', bound=Any)


class LocaleMismatchHookProto(Protocol):
    async def __call__(
        self,
        __method: FunPayMethod[R],
        __bot: 'Bot',
        __response: Response[R],
    ) -> Response[R]:
        pass


class Bot:
    def __init__(
        self,
        golden_key: str,
        session: BaseSession | None = None,
        storage: Storage | None = None,
        *,
        phpsessid: str | None = None,
        proxy: str | None = None,
        default_headers: dict[str, Any] | None = None,
    ) -> None:
        self._golden_key = golden_key
        self._csrf_token: str | None = None
        self._phpsessid: str | None = phpsessid
        self._logout_token: str | None = None

        self._locale: Language | None = None
        self._currency: Currency | None = None

        self._session = session or AioHttpSession(proxy=proxy, default_headers=default_headers)
        self._runner = Runner(self)

        self._storage = storage or InMemoryStorage()

        self._userid: int | None = None
        self._username: str | None = None

        self._session_updated_at = 0

        self._on_locale_mismatch_hook: LocaleMismatchHookProto = force_locale_hook

        self._messages_lock = Lock()
        self._listening_lock = Lock()
        self._stopping_lock = Lock()

        self._stop_event = Event()
        self._stopped_event = Event()

        self._stopped_event.set()

    @property
    def anonymous(self) -> bool:
        """Whether this bot instance is anonymous or not."""
        return not bool(self._golden_key)

    @property
    def initialized(self) -> bool:
        """
        Whether this bot instance is initialized or not.

        To initialize the bot instance, use ``Bot.update`` method.
        """
        to_check: list[Any] = [
            self.csrf_token,
            self.phpsessid,
            self.locale,
            self.currency,
        ]
        if not self.anonymous:
            to_check.extend(
                [
                    self.userid,
                    self.username,
                ],
            )
        return all(bool(i) for i in to_check)

    @property
    def golden_key(self) -> str:
        """
        Golden key (token).
        """
        return self._golden_key

    @property
    def csrf_token(self) -> str | None:
        """
        CSRF token. Available only after initialization (``Bot.update`` method).
        """
        return self._csrf_token

    @property
    def phpsessid(self) -> str | None:
        """
        PHPSESSID. Available only after initialization (``Bot.update`` method).
        """
        return self._phpsessid

    @property
    def logout_token(self) -> str | None:
        """
        Logout token. Available only after initialization (``Bot.update`` method).
        """
        return self._logout_token

    @property
    def userid(self) -> int | None:
        return self._userid

    @property
    def username(self) -> str | None:
        return self._username

    @property
    def locale(self) -> Language | None:
        """
        Bot locale. Available only after initialization (``Bot.update`` method).
        """
        return self._locale

    @property
    def currency(self) -> Currency | None:
        """
        Bot currency. Available only after initialization (``Bot.update`` method).
        """
        return self._currency

    @property
    def session(self) -> BaseSession:
        """
        Bot session.
        """
        return self._session

    @property
    def storage(self) -> Storage:
        return self._storage

    @property
    def session_updated_at(self) -> int:
        return self._session_updated_at

    def set_on_locale_mismatch_hook(self, hook: LocaleMismatchHookProto) -> None:
        self._on_locale_mismatch_hook = hook

    async def runner_request(
        self,
        objects_to_request: Sequence[RequestableObject] | Literal[False] = False,
        action: Action | Literal[False] = False,
    ) -> RunnerResponse:
        """
        Makes request to the runner.
        :return: Runner response.
        """
        return (
            await RunnerRequest(
                objects_to_request=objects_to_request,
                action=action,
            ).execute(self)
        ).response_obj

    # ----- Actions -----
    async def mute_chat(self, chat_id: int, mute: bool) -> bool:
        return (await MuteChat(chat_id=chat_id, mute=mute).execute(self)).response_obj

    async def raise_offers(self, category_id: int, *subcategory_ids: int) -> bool:
        if not subcategory_ids:
            category = await self.storage.get_category(category_id)
            if category is None:
                raise ValueError(f'Category with ID {category_id} not found.')
            subcategory_ids = [
                i.id for i in category.subcategories if i.type is SubcategoryType.COMMON
            ]
        return (
            await RaiseOffers(
                category_id=category_id,
                subcategory_ids=list(subcategory_ids),
            ).execute(self)
        ).response_obj

    async def upload_chat_image(self, file: str | BytesIO) -> int:
        """
        Uploads an image to FunPay servers for use in chat messages.

        The image can later be referenced in chat via its assigned image ID.

        :param file: Path to the image file (as a string) or an in-memory
        file-like object (``BytesIO``).

        :return: Unique FunPay image ID assigned to the uploaded image.
        """
        return (await UploadImage(file=file).execute(self)).response_obj

    async def upload_avatar(self, file: str | BytesIO) -> bool:
        return (await UploadAvatar(file=file).execute(self)).response_obj

    @overload
    async def send_message(
        self,
        chat_id: int | str,
        text: str | None = None,
        image: str | BytesIO | int | None = None,
        enforce_whitespaces: bool = True,
        keep_chat_unread: Literal[False] = False,
    ) -> Message: ...

    @overload
    async def send_message(
        self,
        chat_id: int | str,
        text: str | None = None,
        image: str | BytesIO | int | None = None,
        enforce_whitespaces: bool = True,
        keep_chat_unread: Literal[True] = True,
    ) -> None: ...

    async def send_message(
        self,
        chat_id: int | str,
        text: str | None = None,
        image: str | BytesIO | int | None = None,
        enforce_whitespaces: bool = True,
        keep_chat_unread: bool = False,
    ) -> Message | None:
        """
        Send a message to a chat.

        You must provide **either** a text message or an image — not both.
        The image can be a file path (``str``), a file-like object (``BytesIO``),
        or an existing image ID (``int``).

        .. note::
            By default, FunPay trims the message text and replaces multiple consecutive spaces
            or line breaks with a single space or line break.

            If ``enforce_whitespaces`` is ``True`` (default: ``True``),
            this method preserves the exact number of spaces and line breaks by appending
            an invisible tag ``[a][/a]`` after each one (except the last), preventing FunPay
            from collapsing them.

        :param chat_id: Target chat ID.
        :param text: Text content of the message.
        :param image: Image to send: file path, file-like object, or existing image ID.
        :param enforce_whitespaces: whether to preserve the exact number of spaces and line breaks
            or not. Defaults to ``True``.

        :returns: The resulting message object.
        """

        if not (isinstance(text, str) or isinstance(image, str | BytesIO | int)):
            raise ValueError(
                'Invalid message text or image input: '
                f"either provide message text ('text') (got {text=}), "
                "or provide image ID / path to image / image file stream ('image') "
                f'(got {image=}).',
            )

        if text and image:
            raise ValueError(
                "Invalid arguments: you must provide either 'text' or 'image', not both "
                f'(got {text=!r} and {image=!r}).',
            )

        if image is not None:
            image = (
                image
                if isinstance(image, int)
                else (await UploadImage(image).execute(self)).response_obj
            )
        elif text is not None:
            if enforce_whitespaces:
                text = enforce_message_text_whitespaces(text)
            check_message_text(text)

        msg_data = SendingMessageData(chat_id=chat_id, message_text=text or '', image_id=image)
        objects: Literal[False] | list[Any] = (
            False
            if keep_chat_unread
            else [NodeRequestObject(chat_id=chat_id, runner_tag=random_runner_tag())]
        )

        async with self._messages_lock:
            result = (
                await RunnerRequest(
                    objects_to_request=objects,
                    action=SendMessageAction(message_data=msg_data),
                ).execute(self)
            ).response_obj

            if not keep_chat_unread:
                msg = result.nodes[0].data.messages[-1]
                await self.storage.mark_message_as_sent_by_bot(message_id=msg.id)
                return msg
        return None

    async def refund(self, order_id: str) -> bool:
        return (await Refund(order_id=order_id).execute(self)).response_obj

    async def review(self, order_id: str, text: str, rating: Literal[0, 1, 2, 3, 4, 5]) -> bool:
        return (
            await Review(order_id=order_id, text=text, rating=rating).execute(self)
        ).response_obj

    async def delete_review(self, order_id: str) -> bool:
        return (await DeleteReview(order_id=order_id).execute(self)).response_obj

    async def save_offer_fields(self, offer_fields: OfferFields) -> bool:
        return (await SaveOfferFields(offer_fields=offer_fields).execute(self)).response_obj

    async def calc_chips(self, game_id: int, price: float) -> CalcResult:
        return (await CalcChips(game_id=game_id, price=price).execute(self)).response_obj

    async def calc_lots(self, subcategory_id: int, price: float) -> CalcResult:
        return (
            await CalcLots(subcategory_id=subcategory_id, price=price).execute(self)
        ).response_obj

    async def logout(self) -> bool:
        if self.logout_token is None:
            await self.update()

        return (await Logout(logout_token=self.logout_token).execute(self)).response_obj  # type: ignore # will raise UnauthorizedError after self.update

    async def set_notification_status(self, enabled: bool, channel: NoticeChannel) -> bool:
        return (
            await UpdateNoticeChannel(enabled=enabled, channel=channel).execute(self)
        ).response_obj

    async def set_telegram_notification_status(self, enabled: bool) -> bool:
        return (
            await UpdateNoticeChannel(enabled=enabled, channel=NoticeChannel.TELEGRAM).execute(
                self,
            )
        ).response_obj

    async def set_push_notification_status(self, enabled: bool) -> bool:
        return (
            await UpdateNoticeChannel(enabled=enabled, channel=NoticeChannel.PUSH).execute(self)
        ).response_obj

    async def set_email_notification_status(self, enabled: bool) -> bool:
        return (
            await UpdateNoticeChannel(enabled=enabled, channel=NoticeChannel.EMAIL).execute(
                self,
            )
        ).response_obj

    async def set_offers_hidden(self, hidden: bool) -> bool:
        return (await SetOffersHidden(hidden=hidden).execute(self)).response_obj

    # ----- Runner shortcuts -----
    @overload
    async def get_currently_viewing_offer(
        self,
        *user_ids: int,
        user_id: None = None,
    ) -> dict[int, CurrentlyViewingOfferInfo | bool]: ...

    @overload
    async def get_currently_viewing_offer(
        self,
        *,
        user_id: int,
    ) -> CurrentlyViewingOfferInfo | bool: ...

    async def get_currently_viewing_offer(
        self,
        *user_ids: int,
        user_id: int | None = None,
    ) -> dict[int, CurrentlyViewingOfferInfo | bool] | CurrentlyViewingOfferInfo | bool:
        """
        Returns the last offer that the user has seen recently
        """
        if not user_ids and user_id is None:
            raise ValueError('Either `user_ids` or `user_id` must be provided.')

        if user_ids:
            objects = [CPURequestObject(id=user_id) for user_id in user_ids]
        else:
            objects = [CPURequestObject(id=user_id)]

        response = await self.runner_request(objects_to_request=objects)

        if not response.cpu:
            return {} if user_ids else False

        if user_ids:
            return {cpu.id: cpu.data for cpu in response.cpu}  # type: ignore # todo
        return response.cpu[0].data

    async def get_unread_chats_amount(self) -> int:
        """
        Returns the amount of unread chats
        """
        response = await self.runner_request(objects_to_request=[ChatCounterRequestObject()])

        if not response.chat_counter:
            return 0

        return response.chat_counter.data.counter  # type: ignore # will have data

    async def get_active_orders_amount(self) -> tuple[int, int]:
        """
        Returns the amount of active orders (purchases, sales)
        """
        response = await self.runner_request(objects_to_request=[OrdersCountersRequestObject()])

        if not response.orders_counters:
            return 0, 0

        return response.orders_counters.data.purchases, response.orders_counters.data.sales  # type: ignore # will have data

    async def get_recent_chat_previews(self) -> list[PrivateChatPreview]:
        """
        Returns the list of recent chat previews
        """
        response = await self.runner_request(objects_to_request=[ChatBookmarksRequestObject()])

        if not response.chat_bookmarks:
            return []

        return response.chat_bookmarks.data.chat_previews  # type: ignore # will have data

    @overload
    async def get_chat_messages(
        self,
        *,
        chat_id: int | str,
        after_message_id: int | None = None,
    ) -> list[Message]: ...

    @overload
    async def get_chat_messages(
        self,
        *args: tuple[int | str, int | None],
        chat_id: None = None,
        after_message_id: None = None,
    ) -> dict[int, list[Message]]: ...

    async def get_chat_messages(
        self,
        *args: tuple[int | str, int | None],
        chat_id: int | str | None = None,
        after_message_id: int | None = None,
    ) -> list[Message] | dict[int, list[Message]]:
        """
        Retrieves the 100 most recent messages in a chat,
        sent after the specified message ID.

        :param chat_id: Chat ID.
        :param after_message_id: Message ID to paginate history **forwards from** (exclusive).
            Messages with IDs **greater than** this one will be returned,
            i.e. history will be fetched in forward order *after* this message.

        :param args: Tuple of (chat_id, after_message_id)

        :returns: A dictionary [chat_id, list] or a list of up to 100 ``Message`` objects, sorted from oldest to newest.
        """
        if not args and chat_id is None:
            raise ValueError('Either `chat_id` or `args` must be provided.')

        if args:
            objects = [
                NodeRequestObject(
                    chat_id=arg[0],
                    data=RequestNodeInfo(chat_id=arg[0], after_message_id=arg[1] or 0),
                )
                for arg in args
            ]
        else:
            objects = [
                NodeRequestObject(
                    chat_id=chat_id,
                    data=RequestNodeInfo(chat_id=chat_id, after_message_id=after_message_id or 0),
                ),
            ]

        response = await self.runner_request(objects_to_request=objects)
        if not response.nodes:
            return {} if args else []

        if args:
            return {obj.data.node.id: obj.data.messages for obj in response.nodes}  # type: ignore # todo
        return response.nodes[0].data.messages  # type: ignore # todo

    # ----- Getters -----
    async def get_telegram_connect_url(self) -> str:
        return (await GetTelegramConnectURL().execute(self)).response_obj

    async def get_chat_history(
        self,
        chat_id: int | str,
        before_message_id: int = -1,
    ) -> list[Message]:
        """
        Retrieves the 100 most recent messages in a chat,
        sent before the specified message ID.

        :param chat_id: Chat ID.
        :param before_message_id: Message ID to paginate history **backwards from** (exclusive).
            Messages with IDs **lower than** this one will be returned,
            i.e. history will be fetched in reverse order *before* this message.

        :returns: A list of up to 100 ``Message`` objects, sorted from newest to oldest.
        """
        return (
            await GetChatHistory(chat_id=chat_id, before_message_id=before_message_id).execute(
                self,
            )
        ).response_obj

    async def get_sales(
        self,
        from_order_id: str | None = None,
        order_id_filter: str | None = None,
        buyer_username_filter: str | None = None,
        status_filter: OrderStatus | str | None = None,
        game_id_filter: str | None = None,
        other_filters: dict[str, str] | None = None,
    ) -> OrderPreviewsBatch:
        """
        Fetch the latest 100 sales, optionally filtered by various criteria.

        If ``from_order_id`` is provided,
        the method retrieves sales after the specified order ID, enabling pagination.

        :param from_order_id: Optional. The order ID to start pagination from (inclusive).
        :param order_id_filter: Optional. Only return the sale with this exact order ID.
        :param buyer_username_filter: Optional. Only include sales from this seller.
        :param status_filter: Optional. Only include sales with the specified status.
            Can be an `OrderStatus` enum or a string.
        :param game_id_filter: Optional. Only include sales related to this game ID.
        :param other_filters: Optional. A dictionary of additional filters to apply.

        :return: A batch of order previews (``OrderPreviewsBatch``)
            matching the specified criteria.
        """
        method = GetSales(
            from_order_id=from_order_id,
            order_id_filter=order_id_filter,
            buyer_username_filter=buyer_username_filter,
            status_filter=status_filter,
            game_id_filter=game_id_filter,
            other_filters=other_filters,
        )

        return (await method.execute(self)).response_obj

    async def get_purchases(
        self,
        from_order_id: str | None = None,
        order_id_filter: str | None = None,
        seller_username_filter: str | None = None,
        status_filter: OrderStatus | str | None = None,
        game_id_filter: str | None = None,
        other_filters: dict[str, str] | None = None,
    ) -> OrderPreviewsBatch:
        """
        Fetch the latest 100 purchases, optionally filtered by various criteria.

        If ``from_order_id`` is provided,
        the method retrieves purchases after the specified order ID, enabling pagination.

        :param from_order_id: Optional. The order ID to start pagination from (inclusive).
        :param order_id_filter: Optional. Only return the purchase with this exact order ID.
        :param seller_username_filter: Optional. Only include purchases from this seller.
        :param status_filter: Optional. Only include purchases with the specified status.
            Can be an `OrderStatus` enum or a string.
        :param game_id_filter: Optional. Only include purchases related to this game ID.
        :param other_filters: Optional. A dictionary of additional filters to apply.

        :return: A batch of purchase previews (``OrderPreviewsBatch``)
            matching the specified criteria.
        """
        method = GetPurchases(
            from_order_id=from_order_id,
            order_id_filter=order_id_filter,
            seller_username_filter=seller_username_filter,
            status_filter=status_filter,
            game_id_filter=game_id_filter,
            other_filters=other_filters,
        )

        return (await method.execute(self)).response_obj

    @overload
    async def get_offer_fields(
        self,
        subcategory_type: SubcategoryType = ...,
        subcategory_id: int = ...,
        subcategory: None = ...,
        offer_id: None = ...,
    ) -> OfferFields: ...

    @overload
    async def get_offer_fields(
        self,
        subcategory_type: None = ...,
        subcategory_id: None = ...,
        subcategory: Subcategory = ...,
        offer_id: None = ...,
    ) -> OfferFields: ...

    @overload
    async def get_offer_fields(
        self,
        subcategory_type: None = ...,
        subcategory_id: None = ...,
        subcategory: None = ...,
        offer_id: int = ...,
    ) -> OfferFields: ...

    async def get_offer_fields(
        self,
        subcategory_type: SubcategoryType | None = None,
        subcategory_id: int | None = None,
        subcategory: Subcategory | None = None,
        offer_id: int | None = None,
    ) -> OfferFields:
        # todo: If getting fields of existing offer, no need to pass subcategory type and id.
        if isinstance(subcategory_type, SubcategoryType) and isinstance(subcategory_id, int):
            t, i = subcategory_type, subcategory_id
        elif isinstance(subcategory, Subcategory):
            t, i = subcategory.type, subcategory.id
        elif isinstance(offer_id, int):
            t, i = SubcategoryType.COMMON, 1
        else:
            raise ValueError(
                f'Invalid subcategory input: '
                f"either provide both 'subcategory_type' and 'subcategory_id' "
                f"(got {subcategory_type=}, {subcategory_id=}), or provide 'subcategory' object "
                f'(got {subcategory=}).',
            )

        return (
            await GetOfferFields(
                subcategory_type=t,
                subcategory_id=i,
                offer_id=offer_id,
            ).execute(self)
        ).response_obj

    async def get_transactions(
        self,
        from_transaction_id: int = 0,
        filter: str = '',
    ) -> TransactionPreviewsBatch:
        return (
            await GetTransactions(
                filter=filter,
                from_transaction_id=from_transaction_id,
            ).execute(self)
        ).response_obj

    # ----- Page getters -----
    async def get_main_page(self) -> MainPage:
        """
        Retrieves the FunPay main page.
        """
        return (await GetMainPage().execute(self)).response_obj

    async def get_chat_page(self, chat_id: int | str) -> ChatPage:
        """
        Retrieves the chat page.

        :param chat_id: Chat ID or name.
        """
        return (await GetChatPage(chat_id=chat_id).execute(self)).response_obj

    async def get_profile_page(self, id: int) -> ProfilePage:
        return (await GetProfilePage(user_id=id).execute(self)).response_obj

    async def get_subcategory_page(
        self,
        subcategory_type: SubcategoryType,
        subcategory_id: int,
    ) -> SubcategoryPage:
        return (
            await GetSubcategoryPage(
                type=subcategory_type,
                subcategory_id=subcategory_id,
            ).execute(self)
        ).response_obj

    async def get_my_offers_page(self, subcategory_id: int) -> MyOffersPage:
        return (await GetMyOffersPage(subcategory_id=subcategory_id).execute(self)).response_obj

    async def get_my_chips_page(self, subcategory_id: int) -> MyChipsPage:
        return (await GetMyChipsPage(subcategory_id=subcategory_id).execute(self)).response_obj

    async def get_order_page(self, order_id: str) -> OrderPage:
        return (await GetOrderPage(order_id=order_id).execute(self)).response_obj

    async def get_settings_page(self) -> SettingsPage:
        return (await GetSettingPage().execute(self)).response_obj

    async def get_transactions_page(self) -> TransactionsPage:
        return (await GetTransactionsPage().execute(self)).response_obj

    async def get_settings(self) -> Settings:
        return (await self.get_settings_page()).settings

    async def get_2fa_status(self) -> bool:
        return (await Get2faStatus().execute(self)).response_obj

    async def check_banned(self) -> bool:
        return (await CheckBanned().execute(self)).response_obj

    async def make_request(
        self,
        method: FunPayMethod[MethodReturnType],
        skip_update: bool = False,
        skip_locale_check: bool = False,
        skip_session_cookies: bool = False,
    ) -> Response[MethodReturnType]:
        if not method.allow_anonymous and self.anonymous:
            raise RuntimeError(
                f"Method '{method.__class__.__name__}' cannot be executed anonymously.",
            )

        if not skip_update and (
            not self.initialized or time.time() - self.session_updated_at >= 1200
        ):
            await self.update()

        result = await self.session.make_request(
            method,
            self,
            skip_session_cookies=skip_session_cookies,
        )

        if (
            not skip_locale_check
            and self._locale
            and self._locale != Language.get_by_lang_code(result.locale)
        ):
            result = await self._on_locale_mismatch_hook(method, self, result)

        if isinstance(result.response_obj, FunPayPage):
            if self._golden_key and not result.response_obj.header.avatar_url:
                raise BotUnauthenticatedError()

        if (method.url != 'account/blocked') and ('account/blocked' in result.url):
            raise UserBannedError()

        if 'PHPSESSID' in result.cookies and not skip_update:
            self._phpsessid = result.cookies['PHPSESSID']
            self._session_updated_at = int(time.time())

        return result

    async def update(self, change_locale: Language | None = None) -> Self:
        result = await self.make_request(
            GetMainPage(change_locale=change_locale), skip_update=True, skip_session_cookies=True
        )

        page_obj = result.response_obj

        await self.storage.remove_categories()
        await self.storage.save_categories(*page_obj.categories)
        self._csrf_token = page_obj.app_data.csrf_token
        self._phpsessid = result.cookies.get('PHPSESSID')
        self._logout_token = page_obj.header.logout_token

        if not self._locale or change_locale is not None:
            self._locale = page_obj.app_data.locale

        self._currency = page_obj.header.currency
        self._userid = page_obj.header.user_id
        self._username = page_obj.header.username

        self._session_updated_at = int(time.time())
        return self

    async def _listen_events(
        self,
        dp: Dispatcher,
        /,
        *,
        config: RunnerConfig | None = None,
        session_storage: Storage | None = None,
        workflow_injection: dict[str, Any] | None = None,
    ) -> None:
        workflow_injection = workflow_injection if workflow_injection is not None else {}
        try:
            async with self.session:
                listener = self._runner.listen(config=config, session_storage=session_storage)
                async for event, stack in listener:
                    await dp.event_entry(
                        event,
                        event_context_injection={
                            **workflow_injection,
                            'events_stack': stack,
                            'bot': self,
                        },
                    )
        except KeyboardInterrupt:
            return

    async def listen_events(
        self,
        dp: Dispatcher,
        /,
        *,
        config: RunnerConfig | None = None,
        session_storage: Storage | None = None,
        workflow_injection: dict[str, Any] | None = None,
    ) -> None:
        if self._listening_lock.locked():
            raise RuntimeError('Already listening')

        async with self._listening_lock:
            self._stop_event.clear()
            self._stopped_event.clear()

            tasks = [
                asyncio.create_task(
                    self._listen_events(
                        dp,
                        config=config,
                        session_storage=session_storage,
                        workflow_injection=workflow_injection,
                    ),
                ),
                asyncio.create_task(self._stop_event.wait()),
            ]

            _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                with suppress(asyncio.CancelledError):
                    task.cancel()
            self._stopped_event.set()

    async def stop_listening(self) -> None:
        if self._stopped_event.is_set():
            raise RuntimeError('Listening is already stopped.')
        if self._stopping_lock.locked():
            raise RuntimeError('Listening stopping already in progress.')

        async with self._stopping_lock:
            self._stop_event.set()
            await self._stopped_event.wait()
