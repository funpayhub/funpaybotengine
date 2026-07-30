from __future__ import annotations


__all__ = [
    'NewEventsPack',
    'ChatChanged',
    'NewMessage',
    'OrderEvent',
    'NewSale',
    'SaleStatusChanged',
    'SaleClosed',
    'SaleClosedByAdmin',
    'SaleRefunded',
    'SalePartiallyRefunded',
    'SaleReopened',
    'SaleStatusChanged',
    'NewPurchase',
    'PurchaseStatusChanged',
    'PurchaseClosed',
    'PurchaseClosedByAdmin',
    'PurchaseRefunded',
    'PurchasePartiallyRefunded',
    'PurchaseReopened',
    'ReviewEvent',
    'NewReview',
    'NewReviewReply',
    'ReviewChanged',
    'ReviewReplyChanged',
    'ReviewDeleted',
    'ReviewReplyDeleted',
]


from typing import Any

from pydantic import PrivateAttr

from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.orders import OrderPreview
from funpaybotengine.types.reviews import Review
from funpaybotengine.types.messages import Message
from funpaybotengine.types.pages.order_page import OrderPage

from .base import RunnerEvent, BotEngineEvent


class NewEventsPack(BotEngineEvent[int], event_name='new_events_pack'): ...


class ChatChanged(RunnerEvent[PrivateChatPreview], event_name='chat_changed'):
    old: PrivateChatPreview | None = None

    @property
    def chat_preview(self) -> PrivateChatPreview:
        return self.object

    def context_injection(self) -> dict[str, Any]:
        return super().context_injection() | {'chat_preview': self.chat_preview}


class NewMessage(RunnerEvent[Message], event_name='new_message'):
    @property
    def message(self) -> Message:
        return self.object

    def context_injection(self) -> dict[str, Any]:
        return super().context_injection() | {'message': self.message}


class OrderEvent(NewMessage, event_name='__order_event__'):
    _order_preview: OrderPreview | None = PrivateAttr(default=None)

    async def get_order_preview(self, update: bool = False) -> OrderPreview:
        raise NotImplementedError


class SaleEvent(OrderEvent, event_name='__sale_event__'):
    async def get_order_preview(self, update: bool = False) -> OrderPreview:
        if self._order_preview is not None and not update:
            return self._order_preview

        orders = await self.get_bound_bot().get_sales(order_id_filter=self.object.meta.order_id)
        return orders.orders[0]


class PurchaseEvent(OrderEvent, event_name='__purchase_event__'):
    async def get_order_preview(self, update: bool = False) -> OrderPreview:
        if self._order_preview is not None and not update:
            return self._order_preview

        orders = await self.get_bound_bot().get_purchases(
            order_id_filter=self.object.meta.order_id,
        )
        return orders.orders[0]


class NewSale(SaleEvent, event_name='new_sale'): ...


class SaleStatusChanged(SaleEvent, event_name='sale_status_changed'):
    previous: OrderPreview | None = None


class SaleClosed(SaleStatusChanged, event_name='sale_closed'): ...


class SaleClosedByAdmin(SaleClosed, event_name='sale_closed_by_admin'): ...


class SaleRefunded(SaleStatusChanged, event_name='sale_refunded'): ...


class SalePartiallyRefunded(SaleRefunded, event_name='sale_partially_refunded'): ...


class SaleReopened(SaleStatusChanged, event_name='sale_reopened'): ...


class NewPurchase(PurchaseEvent, event_name='new_purchase'): ...


class PurchaseStatusChanged(PurchaseEvent, event_name='purchase_status_changed'):
    previous: OrderPreview | None = None


class PurchaseClosed(PurchaseStatusChanged, event_name='purchase_closed'): ...


class PurchaseClosedByAdmin(PurchaseClosed, event_name='purchase_closed_by_admin'): ...


class PurchaseRefunded(PurchaseStatusChanged, event_name='purchase_refunded'): ...


class PurchasePartiallyRefunded(PurchaseRefunded, event_name='purchase_partially_refunded'): ...


class PurchaseReopened(PurchaseStatusChanged, event_name='purchase_reopened'): ...


class ReviewEvent(NewMessage, event_name='__review_event__'):
    _order_page: OrderPage | None = PrivateAttr(default=None)

    async def get_order_page(self, update: bool = False) -> OrderPage:
        if self._order_page is None or update:
            bot = self.get_bound_bot()
            self._order_page = await bot.get_order_page(self.object.meta.order_id or '')

        return self._order_page

    async def get_review(self, update: bool = False) -> Review | None:
        order_page = await self.get_order_page(update)
        return order_page.review


class NewReview(ReviewEvent, event_name='new_review'): ...


class ReviewChanged(ReviewEvent, event_name='review_changed'): ...


class ReviewDeleted(ReviewEvent, event_name='review_deleted'): ...


class NewReviewReply(ReviewEvent, event_name='new_review_reply'): ...


class ReviewReplyChanged(ReviewEvent, event_name='review_reply_changed'): ...


class ReviewReplyDeleted(ReviewEvent, event_name='review_reply_deleted'): ...
