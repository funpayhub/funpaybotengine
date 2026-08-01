from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Type, TypeVar
from dataclasses import field, dataclass
from collections import ChainMap, defaultdict
from collections.abc import Callable, Generator

from funpaybotengine.types import Message, PrivateChatPreview
from funpaybotengine.utils import random_runner_tag
from funpaybotengine.loggers import runner_logger as logger
from funpaybotengine.exceptions import UnauthorizedError, BotUnauthenticatedError
from funpaybotengine.dispatching import RunnerEvent
from funpaybotengine.types.enums import OrderType, MessageType
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.storage.inmemory import InMemoryStorage
from funpaybotengine.dispatching.events import builtin_events as be
from funpaybotengine.types.requests.runner import (
    NodeRequestObject,
    ChatBookmarksRequestObject,
    OrdersCountersRequestObject,
)
from funpaybotengine.exceptions.session_exceptions import UnexpectedHTTPStatusError


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
    MessageType.NEW_FEEDBACK_REPLY: be.NewReviewReply,
    MessageType.FEEDBACK_CHANGED: be.ReviewChanged,
    MessageType.FEEDBACK_REPLY_CHANGED: be.ReviewReplyChanged,
    MessageType.FEEDBACK_DELETED: be.ReviewDeleted,
    MessageType.FEEDBACK_REPLY_DELETED: be.ReviewReplyDeleted,
}

_RELATED = _REVIEW_RELATED | _ORDER_RELATED


F = TypeVar('F', bound=Callable[..., Any])
debug = logger.debug


def attempts(amount: int = 0) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        async def inner(*args: Any, **kwargs: Any) -> Any:
            nonlocal amount
            infinite = not amount

            while infinite or amount:
                amount -= 1
                try:
                    return await func(*args, **kwargs)
                except UnauthorizedError:
                    raise
                except UnexpectedHTTPStatusError:
                    if not amount:
                        raise
            return None

        return inner

    return decorator


@dataclass
class MsgUpdate:
    event: be.NewMessage
    related_type: OrderType | None = field(init=False)

    def __post_init__(self) -> None:
        meta = self.event.message.meta
        if meta.type not in _RELATED:
            return

        if meta.type in _REVIEW_RELATED:
            self.event = _REVIEW_RELATED[meta.type](
                object=self.event.message, tag=self.event.tag
            ).as_(self.event.bot)
            return

        bot = self.event.get_bound_bot()
        if meta.buyer_id:
            self.related_type = (
                OrderType.PURCHASE if meta.buyer_id == bot.userid else OrderType.SALE
            )
        elif meta.seller_id:
            self.related_type = (
                OrderType.SALE if meta.seller_id == bot.userid else OrderType.PURCHASE
            )
        else:
            self.related_type = OrderType.UNKNOWN


@dataclass
class ChatUpdate:
    event: be.ChatChanged
    messages: list[MsgUpdate] = field(default_factory=list)

    def add_message(self, event: be.NewMessage) -> None:
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

    def sales_related(self) -> Generator[MsgUpdate, None, None]:
        return (
            m for upd in self.updates for m in upd.messages if m.related_type is OrderType.SALE
        )

    def purchases_related(self) -> Generator[MsgUpdate, None, None]:
        return (
            m for upd in self.updates for m in upd.messages if m.related_type is OrderType.PURCHASE
        )

    def unknown_related(self) -> Generator[MsgUpdate, None, None]:
        return (
            m for upd in self.updates for m in upd.messages if m.related_type is OrderType.UNKNOWN
        )

    def flat(self) -> list[RunnerEvent[Any]]:
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

    def __init__(
        self, bot: Bot, config: RunnerConfig, *, session_storage: Storage | None = None
    ) -> None:
        self.bot = bot
        self.config = config
        self.chats_upd_ts: int | float = time.time()

        self.storage = self.bot.storage
        self.session_storage = session_storage or InMemoryStorage()

    @attempts()
    async def _get_chat_bookmarks(self) -> RunnerResponse:
        async with self.bot._messages_lock:
            result = await self.bot.runner_request(
                objects_to_request=[ChatBookmarksRequestObject(), OrdersCountersRequestObject()],
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

    async def get_new_message_events(self, pack: EventsPack) -> EventsPack:
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
        return pack

    async def resolve_order(
        self, upd: MsgUpdate, orders: dict[OrderType, dict[str, OrderPreview]], discover: OrderType
    ) -> None:
        if (order_id := upd.event.object.meta.order_id) is None:
            raise ValueError()

        if order_id in orders[OrderType.PURCHASE]:
            upd.related_type = OrderType.PURCHASE
        elif order_id in orders[OrderType.SALE]:
            upd.related_type = OrderType.SALE
        elif (order := (await self.storage.get_order_preview(order_id))) is not None:
            upd.related_type = order.type
            orders[upd.related_type][order_id] = order

        if upd.related_type is OrderType.UNKNOWN:
            if discover is OrderType.SALE and self.config.discover_sales:
                order_tuple = await self._get_sales(order_id=upd.event.object.meta.order_id)
            elif discover is OrderType.PURCHASE and self.config.discover_purchases:
                order_tuple = await self._get_purchases(order_id=upd.event.object.meta.order_id)
            else:
                return

            if not order_tuple:
                return

            upd.related_type = discover
            orders[discover][order_id] = order_tuple[0]

        cls = _ORDER_RELATED[upd.event.message.meta.type][
            0 if upd.related_type is OrderType.SALE else 1
        ]
        e = cls(object=upd.event.object, tag=upd.event.tag).as_(self.bot)
        e._order_preview = ChainMap(*orders.values()).get(order_id)
        upd.event = e

    async def gen_order_events(self, pack: EventsPack) -> EventsPack:
        orders: dict[OrderType, dict[str, OrderPreview]] = defaultdict(dict)

        if self.config.discover_sales:
            orders[OrderType.SALE] = {i.id: i for i in await self._get_sales()}

        for upd in list(pack.sales_related()) + list(pack.unknown_related()):
            await self.resolve_order(upd, orders, OrderType.SALE)

        for upd in list(pack.purchases_related()) + list(pack.unknown_related()):
            await self.resolve_order(upd, orders, OrderType.PURCHASE)

        return pack

    async def get_events(self) -> list[RunnerEvent[Any]]:
        debug('Getting events...')

        r = await self.get_chat_changed_events()
        if not r:
            return []

        r = await self.get_new_message_events(r)
        r = await self.gen_order_events(r)
        result = r.flat()

        await self.session_storage.save_chat_previews(*(i.event.chat_preview for i in r.updates))
        await self.storage.save_order_previews(
            *(
                e._order_preview
                for e in result
                if isinstance(e, be.OrderEvent) and e._order_preview is not None
            )
        )

        self.chats_upd_ts = r.timestamp
        return r.flat()
