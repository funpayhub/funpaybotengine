from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Type, Literal, TypeVar, cast
from itertools import chain
from collections.abc import Callable

from funpaybotengine.types import PrivateChatPreview
from funpaybotengine.utils import random_runner_tag
from funpaybotengine.loggers import runner_logger as logger
from funpaybotengine.exceptions import UnauthorizedError, BotUnauthenticatedError
from funpaybotengine.dispatching import RunnerEvent
from funpaybotengine.types.enums import MessageType, OrderPreviewType
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.types.messages import Message
from funpaybotengine.storage.inmemory import InMemoryStorage
from funpaybotengine.types.requests.runner import (
    NodeRequestObject,
    ChatBookmarksRequestObject,
    OrdersCountersRequestObject,
)
from funpaybotengine.exceptions.session_exceptions import UnexpectedHTTPStatusError
from funpaybotengine.dispatching.events.builtin_events import (
    SaleEvent,
    OrderEvent,
    ReviewEvent,
    NewSaleEvent,
    PurchaseEvent,
    NewReviewEvent,
    NewMessageEvent,
    SaleClosedEvent,
    ChatChangedEvent,
    NewPurchaseEvent,
    SaleRefundedEvent,
    SaleReopenedEvent,
    ReviewChangedEvent,
    ReviewDeletedEvent,
    PurchaseClosedEvent,
    PurchaseRefundedEvent,
    PurchaseReopenedEvent,
    NewReviewResponseEvent,
    SaleClosedByAdminEvent,
    PurchaseClosedByAdminEvent,
    ReviewResponseChangedEvent,
    ReviewResponseDeletedEvent,
    SalePartiallyRefundedEvent,
    PurchasePartiallyRefundedEvent,
)


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.storage.base import Storage
    from funpaybotengine.types.orders import OrderPreview
    from funpaybotengine.types.updates import RunnerResponse
from collections import ChainMap


CHAT_EVENTS = ChatChangedEvent | NewMessageEvent


_KNOWN_ORDER_RELATED: dict[MessageType, tuple[Type[SaleEvent], Type[PurchaseEvent]]] = {
    MessageType.NEW_ORDER: (NewSaleEvent, NewPurchaseEvent),
    MessageType.ORDER_CLOSED: (SaleClosedEvent, PurchaseClosedEvent),
    MessageType.ORDER_CLOSED_BY_ADMIN: (SaleClosedByAdminEvent, PurchaseClosedByAdminEvent),
}

_UNKNOWN_ORDER_RELATED: dict[MessageType, tuple[Type[SaleEvent], Type[PurchaseEvent]]] = {
    MessageType.ORDER_REFUNDED: (SaleRefundedEvent, PurchaseRefundedEvent),
    MessageType.ORDER_PARTIALLY_REFUNDED: (
        SalePartiallyRefundedEvent,
        PurchasePartiallyRefundedEvent,
    ),
    MessageType.ORDER_REOPENED: (SaleReopenedEvent, PurchaseReopenedEvent),
}

_REVIEW_RELATED: dict[MessageType, Type[ReviewEvent]] = {
    MessageType.NEW_FEEDBACK: NewReviewEvent,
    MessageType.NEW_FEEDBACK_REPLY: NewReviewResponseEvent,
    MessageType.FEEDBACK_CHANGED: ReviewChangedEvent,
    MessageType.FEEDBACK_REPLY_CHANGED: ReviewResponseChangedEvent,
    MessageType.FEEDBACK_DELETED: ReviewDeletedEvent,
    MessageType.FEEDBACK_REPLY_DELETED: ReviewResponseDeletedEvent,
}

_ORDER_RELATED = _KNOWN_ORDER_RELATED | _UNKNOWN_ORDER_RELATED
_RELATED = _REVIEW_RELATED | _ORDER_RELATED


F = TypeVar('F', bound=Callable[..., Any])


def attempts(amount: int = 0) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        async def inner(*args: Any, **kwargs: Any) -> Any:
            attempts = amount or float('inf')
            while attempts:
                attempts -= 1
                try:
                    return await func(*args, **kwargs)
                except UnauthorizedError:
                    raise
                except UnexpectedHTTPStatusError:
                    if not attempts:
                        raise

        return inner  # type: ignore

    return decorator


class EventsPack:
    def __init__(self, timestamp: int | float) -> None:
        # {
        #   ChatChangedEvent: {
        #    NewMessageEvent: Related order/review event or None,
        #    NewMessageEvent2: Related order/review event or None,
        #   },
        #   ChatChangedEvent2: { ... }
        self.tree: dict[
            ChatChangedEvent,
            dict[NewMessageEvent, OrderEvent | ReviewEvent | None],
        ] = {}
        self.sales_related: list[NewMessageEvent] = []
        self.purchases_related: list[NewMessageEvent] = []
        self.unknown_order_related: list[NewMessageEvent] = []
        self.review_related: list[NewMessageEvent] = []
        self.timestamp = timestamp

    @property
    def chainmap(self) -> ChainMap[NewMessageEvent, OrderEvent | ReviewEvent | None]:
        return ChainMap(*self.tree.values())

    @property
    def total_events(self) -> list[RunnerEvent[Any]]:
        total: list[RunnerEvent[Any]] = []
        for chat_event, dict_ in self.tree.items():
            total.append(chat_event)
            for message_event, from_message_event in dict_.items():
                total.append(message_event)
                if from_message_event is not None:
                    total.append(from_message_event)
        return total

    def add_chat_event(self, event: ChatChangedEvent) -> None:
        self.tree[event] = {}

    def add_message_event(self, c: ChatChangedEvent, e: NewMessageEvent, /) -> None:
        meta = e.message.meta
        bot = e.get_bound_bot()
        if meta.type not in _RELATED:
            self.tree[c][e] = None
            return

        if meta.type in _REVIEW_RELATED:
            cls = _REVIEW_RELATED[meta.type]
            review_event = cls(object=e.message, tag=e.tag, related_new_message_event=e).as_(bot)
            self.tree[c][e] = review_event
            return

        # if in order_related
        buyer_id, seller_id, uid = meta.buyer_id, meta.seller_id, bot.userid
        if buyer_id:
            self.purchases_related.append(e) if buyer_id == uid else self.sales_related.append(e)
        elif meta.seller_id:
            self.sales_related.append(e) if seller_id == uid else self.purchases_related.append(e)
        else:
            self.unknown_order_related.append(e)
        self.tree[c][e] = None


class EventCollector:
    """
    Collects updates from FunPay and transforms them into update objects
    compatible with funpaybotengine.
    """

    def __init__(
        self,
        bot: Bot,
        config: RunnerConfig,
        *,
        session_storage: Storage | None = None,
    ) -> None:
        self.bot = bot
        self.config = config
        self.last_chats_request_timestamp: int | float = time.time()

        self.storage = self.bot.storage
        self.session_storage = session_storage or InMemoryStorage()

    @attempts()
    async def _get_chat_bookmarks(self) -> RunnerResponse:
        async with self.bot._messages_lock:
            result = await self.bot.runner_request(
                objects_to_request=[
                    ChatBookmarksRequestObject(),
                    OrdersCountersRequestObject(),
                ],
            )
            if not result.orders_counters or not result.orders_counters.data:
                raise BotUnauthenticatedError()
            return result

    @attempts()
    async def _get_sales(self, order_id: str | None = None) -> tuple[OrderPreview, ...]:
        return (await self.bot.get_sales(order_id_filter=order_id)).orders

    @attempts()
    async def _get_purchases(self, order_id: str | None = None) -> tuple[OrderPreview, ...]:
        return (await self.bot.get_purchases(order_id_filter=order_id)).orders

    @attempts()
    async def _get_node(self, objs: list[NodeRequestObject]) -> RunnerResponse:
        return await self.bot.runner_request(objects_to_request=objs)

    @attempts()
    async def _get_chat_history(self, chat_id: int) -> list[Message]:
        return await self.bot.get_chat_history(chat_id=chat_id)

    async def get_chat_histories(self, chat_ids: list[int]) -> dict[int, list[Message]]:
        messages: dict[int, list[Message]] = {}

        if self.config.keep_unread:
            for i in chat_ids:
                messages |= {i: await self._get_chat_history(i)}
            return messages

        objs = [NodeRequestObject(chat_id=i, runner_tag=random_runner_tag()) for i in chat_ids]
        for i in range(0, len(objs), 10):
            result = await self._get_node(objs[i : i + 10])
            if not result.nodes:
                return {}

            for j in result.nodes:
                if not j.data or not j.data.node:  # just explicit check for mypy.
                    continue
                messages[j.data.node.id] = j.data.messages
        return messages

    async def init_chats(self) -> None:
        logger.debug('Initializing chats...')
        result = await self._get_chat_bookmarks()
        self.last_chats_request_timestamp = result.timestamp

        if not result.chat_bookmarks:
            return

        chat_previews: list[PrivateChatPreview] = result.chat_bookmarks.data.chat_previews  # type: ignore[union-attr] # ->
        # -> chat_bookmarks will not be `False`. If chat_bookmarks is `False`
        # UnauthorizedError should be already raised.

        for i in chat_previews:
            logger.debug(
                f'Chat {i.id} ({i.username}) initialized. Last message ID: {i.last_message_id}',
            )
        await self.session_storage.save_chat_previews(*chat_previews)

    async def get_chat_changed_events(self) -> EventsPack | None:
        logger.debug('Fetching chat previews...')
        runner_response = await self._get_chat_bookmarks()
        if not runner_response.chat_bookmarks or not runner_response.chat_bookmarks.data:
            logger.debug('No chats fetched.')
            return None

        logger.debug('Fetched %r chats.', len(runner_response.chat_bookmarks.data.chat_previews))
        result = EventsPack(timestamp=runner_response.timestamp)
        cached_chat_previews = await self.session_storage.get_chat_previews(
            *(i.id for i in runner_response.chat_bookmarks.data.chat_previews),
        )
        logger.debug('Fetched %r cached chats.', len(cached_chat_previews))

        for cached_chat, chat_preview in zip(
            reversed(cached_chat_previews),
            reversed(runner_response.chat_bookmarks.data.chat_previews),
        ):
            if cached_chat and cached_chat.last_message_id == chat_preview.last_message_id:
                logger.debug(
                    "Chat %r (%r) hasn't changed since last runner request.",
                    chat_preview.id,
                    chat_preview.username,
                )
                continue

            logger.debug(
                'Chat %r (%r) has changed since last runner request: %r -> %r',
                chat_preview.id,
                chat_preview.username,
                cached_chat.last_message_id if cached_chat else -1,
                chat_preview.last_message_id,
            )
            event = ChatChangedEvent(
                previous=cached_chat,
                object=chat_preview,
                tag=runner_response.chat_bookmarks.tag,
            ).as_(self.bot)

            result.add_chat_event(event)

        logger.debug('Total chat changed events: %r', len(result.tree))
        logger.debug(
            'Total changed chats: %r.',
            ', '.join(i.chat_preview.username for i in result.tree.keys()),
        )
        return result

    async def get_new_message_events(self, total: EventsPack) -> None:
        ids = [i.object.id for i in total.tree]
        logger.debug('Getting new messages for chats %s', ', '.join(str(i) for i in ids))
        chat_histories = await self.get_chat_histories(ids)

        for chat_event, dict_ in total.tree.items():
            logger.debug('Processing chat %r...', chat_event.chat_preview.id)
            from_id = chat_event.previous.last_message_id if chat_event.previous else 0
            to_id = chat_event.object.last_message_id
            logger.debug(
                'IDs range for chat %r: %r-%r',
                chat_event.chat_preview.id,
                from_id,
                to_id,
            )

            for message in chat_histories[chat_event.chat_preview.id]:
                if from_id != 0:
                    if from_id < message.id <= to_id:
                        logger.debug(
                            'New message in chat %r (%r): %r '
                            '(from IDs difference: %r < %r <= %r).',
                            chat_event.chat_preview.username,
                            chat_event.chat_preview.id,
                            message.id,
                            from_id,
                            message.id,
                            to_id,
                        )
                    else:
                        logger.debug(
                            'Message %r from chat %r (%r) is not new (from IDs difference: '
                            'not (%r < %r <= %r).',
                            message.id,
                            chat_event.chat_preview.username,
                            chat_event.chat_preview.id,
                            from_id,
                            message.id,
                            to_id,
                        )
                        continue
                elif (
                    message.timestamp >= self.last_chats_request_timestamp and message.id <= to_id
                ):
                    logger.debug('There is no cached cha')
                    logger.debug(
                        'New message in chat %s: %s (from timestamp difference: %s >= %s).',
                        chat_event.chat_preview.id,
                        message.id,
                        message.timestamp,
                        self.last_chats_request_timestamp,
                    )
                else:
                    continue

                message_event = NewMessageEvent(object=message, tag=None).as_(self.bot)
                total.add_message_event(chat_event, message_event)

    async def resolve_unknown_order_related_event(
        self,
        total: EventsPack,
        unknown: NewMessageEvent,
        sale_previews: dict[str, OrderPreview],
        purchase_previews: dict[str, OrderPreview],
    ) -> None:
        if unknown.object.meta.order_id in purchase_previews:
            total.purchases_related.append(unknown)
            return
        if unknown.object.meta.order_id in sale_previews:
            total.sales_related.append(unknown)
            return

        saved_order = await self.storage.get_order_preview(unknown.object.meta.order_id)  # type: ignore[arg-type]
        if saved_order and saved_order.type is not OrderPreviewType.UNKNOWN:
            if saved_order.type is OrderPreviewType.PURCHASE:
                total.purchases_related.append(unknown)
                purchase_previews[saved_order.id] = saved_order
            elif saved_order.type is OrderPreviewType.SALE:
                total.sales_related.append(unknown)
                sale_previews[saved_order.id] = saved_order
            return

        if self.config.discover_sales:
            order_preview = await self._get_sales(order_id=unknown.object.meta.order_id)
            if order_preview:
                total.sales_related.append(unknown)
                sale_previews[order_preview[0].id] = order_preview[0]
                await self.storage.save_order_previews(order_preview[0])
                return

        if self.config.discover_purchases:
            order_preview = await self._get_purchases(order_id=unknown.object.meta.order_id)
            if order_preview:
                total.purchases_related.append(unknown)
                purchase_previews[order_preview[0].id] = order_preview[0]
                await self.storage.save_order_previews(order_preview[0])
                return

    async def _make_order_events(
        self,
        total: EventsPack,
        order_previews: dict[str, OrderPreview],
        mode: Literal['sales', 'purchases'] = 'sales',
    ) -> None:
        for e in total.sales_related if mode == 'sales' else total.purchases_related:
            cls = _ORDER_RELATED[e.object.meta.type][0 if mode == 'sales' else 1]
            order_event: OrderEvent = cls(
                related_new_message_event=e, object=e.object, tag=e.tag
            ).as_(self.bot)

            order_event._order_preview = order_previews.get(e.object.meta.order_id or '')
            for i in total.tree.values():
                if e in i:
                    i[e] = order_event
                    break

    async def make_order_events(self, total: EventsPack) -> None:
        sales, purchases = {}, {}

        if (
            total.purchases_related or total.unknown_order_related
        ) and self.config.discover_purchases:
            purchases = {i.id: i for i in await self._get_purchases()}

        if (total.sales_related or total.unknown_order_related) and self.config.discover_sales:
            sales = {i.id: i for i in await self._get_sales()}

        for e in total.unknown_order_related:
            await self.resolve_unknown_order_related_event(total, e, sales, purchases)

        await self._make_order_events(total, sales, 'sales')
        await self._make_order_events(total, purchases, 'purchases')

    async def get_events(self) -> list[RunnerEvent[Any]]:
        logger.debug('Getting events...')

        total = await self.get_chat_changed_events()
        if not total:
            return []

        await self.get_new_message_events(total)
        await self.make_order_events(total)
        events = total.total_events

        logger.debug('Finished getting events. Total events: %s', len(events))

        # Caching current state (fetched chat and order preview)
        # only after successful requests-bound job.
        await self.session_storage.save_chat_previews(*(i.object for i in total.tree))

        order_events_mapping = {}
        cm = total.chainmap
        for order_related in chain(total.sales_related, total.purchases_related):
            order_event: OrderEvent | None = cast(OrderEvent | None, cm[order_related])
            if order_event is not None and order_event._order_preview is not None:
                order_events_mapping[order_event._order_preview.id] = order_event._order_preview

        for k in order_events_mapping.values():
            await self.storage.save_order_previews(k)

        self.last_chats_request_timestamp = total.timestamp
        return events
