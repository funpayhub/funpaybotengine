from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Type, Literal, TypeVar
from dataclasses import field, dataclass
from itertools import chain
from collections.abc import Callable

from funpaybotengine.types import PrivateChatPreview, Message
from funpaybotengine.utils import random_runner_tag
from funpaybotengine.loggers import runner_logger as logger
from funpaybotengine.exceptions import UnauthorizedError, BotUnauthenticatedError
from funpaybotengine.dispatching import RunnerEvent
from funpaybotengine.types.enums import MessageType, OrderPreviewType
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.storage.inmemory import InMemoryStorage
from funpaybotengine.types.requests.runner import (
    NodeRequestObject,
    ChatBookmarksRequestObject,
    OrdersCountersRequestObject,
)
from funpaybotengine.exceptions.session_exceptions import UnexpectedHTTPStatusError
from funpaybotengine.dispatching.events import builtin_events as be


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.storage.base import Storage
    from funpaybotengine.types.orders import OrderPreview
    from funpaybotengine.types.updates import RunnerResponse


_ORDER_RELATED: dict[MessageType, tuple[Type[be.OrderEvent], Type[be.OrderEvent]]] = {
    MessageType.NEW_ORDER: (be.NewSale, be.NewPurchase),
    MessageType.ORDER_CLOSED: (be.SaleClosed, be.PurchaseClosed),
    MessageType.ORDER_CLOSED_BY_ADMIN: (be.SaleClosedByAdmin, be.PurchaseClosedByAdmin),
    MessageType.ORDER_REFUNDED: (be.SaleRefunded, be.PurchaseRefunded),
    MessageType.ORDER_PARTIALLY_REFUNDED: (be.SalePartiallyRefunded, be.PurchasePartiallyRefunded),
    MessageType.ORDER_REOPENED: (be.SaleReopened, be.PurchaseReopened),
}

_REVIEW_RELATED: dict[MessageType, Type[be.ReviewEvent]] = {
    MessageType.NEW_FEEDBACK: be.NewReview,
    MessageType.NEW_FEEDBACK_REPLY: be.NewReviewResponse,
    MessageType.FEEDBACK_CHANGED: be.ReviewChanged,
    MessageType.FEEDBACK_REPLY_CHANGED: be.ReviewResponseChanged,
    MessageType.FEEDBACK_DELETED: be.ReviewDeleted,
    MessageType.FEEDBACK_REPLY_DELETED: be.ReviewResponseDeleted,
}

_RELATED = _REVIEW_RELATED | _ORDER_RELATED


F = TypeVar('F', bound=Callable[..., Any])
debug = logger.debug


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
        return inner
    return decorator


@dataclass
class MsgUpdate:
    event: be.NewMessage
    related_type: Literal['sale', 'purchase', 'unknown'] | None = None

    def __post_init__(self) -> None:
        meta = self.event.message.meta
        if meta.type not in _RELATED:
            return

        if meta.type in _REVIEW_RELATED:
            self.event = _REVIEW_RELATED[meta.type](object=self.event.message, tag=self.event.tag)
            return

        bot = self.event.get_bound_bot()
        if meta.buyer_id:
            self.related_type = 'purchase' if meta.buyer_id == bot.userid else 'sale'
        elif meta.seller_id:
            self.related_type = 'sale' if meta.seller_id == bot.userid else 'purchase'
        else:
            self.related_type = 'unknown'


@dataclass
class ChatUpdate:
    event: be.ChatChanged
    messages: list[MsgUpdate] = field(default_factory=list)

    def add_message(self, event: be.NewMessage):
        self.messages.append(MsgUpdate(event))

    @property
    def id(self) -> tuple[int, str]:
        return self.event.object.id, self.event.object.username


class EventsPack:
    def __init__(self, timestamp: int | float) -> None:
        self.timestamp = timestamp
        self.updates: list[ChatUpdate] = []

    def add_chat(self, event: be.ChatChanged) -> None:
        self.updates.append(ChatUpdate(event))

    def sales_related(self):
        return (m for upd in self.updates for m in upd.messages if m.related_type == 'sale')

    def purchases_related(self):
        return (m for upd in self.updates for m in upd.messages if m.related_type == 'purchase')

    def unknown_related(self):
        return (m for upd in self.updates for m in upd.messages if m.related_type == 'unknown')

    def flat(self) -> list[RunnerEvent]:
        result = []
        for upd in self.updates:
            result.append(upd.event)
            for msg in upd.messages:
                result.append(msg.event)
        return result



class EventCollector:
    """
    Collects updates from FunPay and transforms them into update objects
    compatible with funpaybotengine.
    """

    def __init__(self, bot: Bot, config: RunnerConfig, *, session_storage: Storage | None = None) -> None:
        self.bot = bot
        self.config = config
        self.chats_upd_ts: int | float = time.time()

        self.storage = self.bot.storage
        self.session_storage = session_storage or InMemoryStorage()

    @attempts()
    async def _get_chat_bookmarks(self) -> RunnerResponse:
        async with self.bot._messages_lock:
            result = await self.bot.runner_request(
                objects_to_request=[ ChatBookmarksRequestObject(), OrdersCountersRequestObject()],
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
        debug('Initializing chats...')
        result = await self._get_chat_bookmarks()
        self.chats_upd_ts = result.timestamp
        if not result.chat_bookmarks:
            return

        chat_previews: list[PrivateChatPreview] = result.chat_bookmarks.data.chat_previews  # type: ignore[union-attr] # ->
        # -> chat_bookmarks will not be `False`. If chat_bookmarks is `False`
        # UnauthorizedError should be already raised.

        for i in chat_previews:
            debug('Chat %d/%s initialized. Last msg: %d.', i.id, i.username, i.last_message_id)
        await self.session_storage.save_chat_previews(*chat_previews)

    async def get_chat_changed_events(self) -> EventsPack | None:
        debug('Fetching chat previews...')
        resp = await self._get_chat_bookmarks()
        if not resp.chat_bookmarks or not resp.chat_bookmarks.data:
            debug('No chats fetched.')
            return None
        chats = resp.chat_bookmarks.data.chat_previews
        tag = resp.chat_bookmarks.tag

        debug('Fetched %d chats.', len(chats))
        cached_chats = await self.session_storage.get_chat_previews(*(i.id for i in chats))
        debug('Fetched %d cached chats.', len(cached_chats))

        result = EventsPack(resp.timestamp)
        for old, new in zip(reversed(cached_chats), reversed(chats)):
            if old and old.last_message_id == new.last_message_id:
                debug("Chat %d/%s hasn't changed.", new.id, new.username)
                continue

            c_last = old.last_message_id if old else -1
            debug('New chat %d/%s: %d->%d.', new.id, new.username, c_last, new.last_message_id)
            result.add_chat(be.ChatChanged(old=old, object=new, tag=tag).as_(self.bot))

        debug('Total chats changed: %r', len(result.updates))
        debug('Changed chats: %r.', ', '.join(str(i.id) for i in result.updates))
        return result

    async def get_new_message_events(self, pack: EventsPack) -> None:
        ids = [i.event.object.id for i in pack.updates]
        debug('Getting new messages for chats %s', ', '.join(str(i) for i in ids))
        chat_histories = await self.get_chat_histories(ids)

        for upd in pack.updates:
            debug('Processing chat %r...', upd.event.chat_preview.id)
            from_ = upd.event.old.last_message_id if upd.event.old else 0
            to = upd.event.object.last_message_id
            debug('IDs range for chat %r: %r-%r', upd.event.chat_preview.id, from_, to)

            for m in chat_histories[upd.event.chat_preview.id]:
                if from_:
                    if not (from_ < m.id <= to):
                        debug('Msg %d@%d/%s: out of IDs range (%d, %d).', m.id, *upd.id, from_, to)
                        continue
                    debug('Msg %d@%d/%s: inside IDs range (%d, %d).', m.id, *upd.id, from_, to)

                elif m.timestamp >= self.chats_upd_ts and m.id <= to:
                    debug('Msg %d@%d/%s: ts %d >= %d).', m.id, *upd.id, m.ts, self.chats_upd_ts)
                else:
                    continue
                upd.add_message(be.NewMessage(object=m, tag=None).as_(self.bot))

    async def resolve_order(self, upd: MsgUpdate, sales: dict[str, OrderPreview], purchases: dict[str, OrderPreview], discover: Literal['sale', 'purchase']) -> None:
        if upd.event.object.meta.order_id in purchases:
            upd.related_type = 'purchase'
            return
        if upd.event.object.meta.order_id in sales:
            upd.related_type = 'sale'
            return

        order = await self.storage.get_order_preview(upd.object.meta.order_id)  # type: ignore[arg-type]
        if order and order.type is not OrderPreviewType.UNKNOWN:
            upd.related_type = 'sale' if order.type is OrderPreviewType.SALE else 'purchase'
            (sales if upd.related_type == 'sale' else purchases)[order.id] = order
            return

        order_preview = None
        if discover == 'sale' and self.config.discover_sales:
            order_preview = await self._get_sales(order_id=upd.event.object.meta.order_id)
        elif discover == 'purchase' and self.config.discover_purchases:
            order_preview = await self._get_purchases(order_id=upd.event.object.meta.order_id)

        if not order_preview:
            return
        order_preview = order_preview[0]

        upd.related_type = discover
        (sales if discover=='sale' else purchases)[order_preview.id] = order_preview

    async def _make_order_events(self, pack: EventsPack, orders: dict[str, OrderPreview]) -> None:
        for u in chain(pack.sales_related(), pack.purchases_related()):
            cls = _ORDER_RELATED[u.event.object.meta.type][0 if u.related_type == 'sale' else 1]
            e = cls(object=u.event.object, tag=u.event.tag).as_(self.bot)
            e._order_preview = orders.get(u.event.object.meta.order_id or '')
            u.event = e

    async def make_order_events(self, pack: EventsPack) -> None:
        sales, purchases = {}, {}
        unknown = list(pack.unknown_related())

        if (list(pack.sales_related()) or unknown) and self.config.discover_sales:
            sales = {i.id: i for i in await self._get_sales()}
            for e in unknown:
                await self.resolve_order(e, sales, purchases, 'sale')
            unknown = list(pack.unknown_related())

        if (list(pack.purchases_related()) or unknown) and self.config.discover_purchases:
            purchases = {i.id: i for i in await self._get_sales()}
            for e in unknown:
                await self.resolve_order(e, sales, purchases, 'purchase')

        await self._make_order_events(pack, sales | purchases)

    async def get_events(self) -> list[RunnerEvent[Any]]:
        debug('Getting events...')

        total = await self.get_chat_changed_events()
        if not total:
            return []

        await self.get_new_message_events(total)
        await self.make_order_events(total)
        await self.session_storage.save_chat_previews(*(i.event.object for i in total.updates))

        await self.storage.save_order_previews(*(
            msg.event._order_preview
            for chat in total.updates
            for msg in chat.messages
            if isinstance(msg.event, be.OrderEvent) and msg.event._order_preview is not None
        ))

        self.chats_upd_ts = total.timestamp
        return total.flat()
