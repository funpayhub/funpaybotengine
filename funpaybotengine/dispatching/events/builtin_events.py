from __future__ import annotations


__all__ = [
    'NewEventsPack',
    'ChatChangedEvent',
    'NewMessageEvent',
    'OrderEvent',
    'NewSaleEvent',
    'SaleStatusChangedEvent',
    'SaleClosedEvent',
    'SaleClosedByAdminEvent',
    'SaleRefundedEvent',
    'SalePartiallyRefundedEvent',
    'SaleReopenedEvent',
    'SaleStatusChangedEvent',
    'NewPurchaseEvent',
    'PurchaseStatusChangedEvent',
    'PurchaseClosedEvent',
    'PurchaseClosedByAdminEvent',
    'PurchaseRefundedEvent',
    'PurchasePartiallyRefundedEvent',
    'PurchaseReopenedEvent',
    'ReviewEvent',
    'NewReviewEvent',
    'NewReviewResponseEvent',
    'ReviewChangedEvent',
    'ReviewResponseChangedEvent',
    'ReviewDeletedEvent',
    'ReviewResponseDeletedEvent',
]


from typing import Any

from pydantic import Field, PrivateAttr

from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.orders import OrderPreview
from funpaybotengine.types.reviews import Review
from funpaybotengine.types.messages import Message
from funpaybotengine.types.pages.order_page import OrderPage

from .base import RunnerEvent, BotEngineEvent


class NewEventsPack(BotEngineEvent[str], event_name='new_events_pack'): ...


class ChatChangedEvent(RunnerEvent[PrivateChatPreview], event_name='chat_changed'):
    previous: PrivateChatPreview | None = None

    @property
    def chat_preview(self) -> PrivateChatPreview:
        return self.object

    def context_injection(self) -> dict[str, Any]:
        return super().context_injection() | {'chat_preview': self.chat_preview}


class NewMessageEvent(RunnerEvent[Message], event_name='new_message'):
    @property
    def message(self) -> Message:
        return self.object

    def context_injection(self) -> dict[str, Any]:
        return super().context_injection() | {'message': self.message}


class FromMessageEvent(NewMessageEvent, event_name='__from_message__'):
    related_new_message_event: NewMessageEvent

    def context_injection(self) -> dict[str, Any]:
        return super().context_injection() | {'new_message_event': self.related_new_message_event}


class OrderEvent(FromMessageEvent, event_name='__order_event__'):
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


class NewSaleEvent(SaleEvent, event_name='new_sale'):
    related_auto_message_events: list[NewMessageEvent] = Field(default_factory=list)


class SaleStatusChangedEvent(SaleEvent, event_name='sale_status_changed'):
    previous: OrderPreview | None = None


class SaleClosedEvent(SaleStatusChangedEvent, event_name='sale_closed'): ...


class SaleClosedByAdminEvent(SaleClosedEvent, event_name='sale_closed_by_admin'): ...


class SaleRefundedEvent(SaleStatusChangedEvent, event_name='sale_refunded'): ...


class SalePartiallyRefundedEvent(SaleRefundedEvent, event_name='sale_partially_refunded'): ...


class SaleReopenedEvent(SaleStatusChangedEvent, event_name='sale_reopened'): ...


class NewPurchaseEvent(PurchaseEvent, event_name='new_purchase'):
    related_auto_message_events: list[NewMessageEvent] = Field(default_factory=list)


class PurchaseStatusChangedEvent(PurchaseEvent, event_name='purchase_status_changed'):
    previous: OrderPreview | None = None


class PurchaseClosedEvent(PurchaseStatusChangedEvent, event_name='purchase_closed'): ...


class PurchaseClosedByAdminEvent(PurchaseClosedEvent, event_name='purchase_closed_by_admin'): ...


class PurchaseRefundedEvent(PurchaseStatusChangedEvent, event_name='purchase_refunded'): ...


class PurchasePartiallyRefundedEvent(
    PurchaseRefundedEvent, event_name='purchase_partially_refunded'
): ...


class PurchaseReopenedEvent(PurchaseStatusChangedEvent, event_name='purchase_reopened'): ...


class ReviewEvent(FromMessageEvent, event_name='__review_event__'):
    _order_page: OrderPage | None = PrivateAttr(default=None)

    async def get_order_page(self, update: bool = False) -> OrderPage:
        if self._order_page is None or update:
            bot = self.get_bound_bot()
            self._order_page = await bot.get_order_page(self.object.meta.order_id or '')

        return self._order_page

    async def get_review(self, update: bool = False) -> Review | None:
        order_page = await self.get_order_page(update)
        return order_page.review


class NewReviewEvent(ReviewEvent, event_name='new_review'): ...


class ReviewChangedEvent(ReviewEvent, event_name='review_changed'): ...


class ReviewDeletedEvent(ReviewEvent, event_name='review_deleted'): ...


class NewReviewResponseEvent(ReviewEvent, event_name='new_review_response'): ...


class ReviewResponseChangedEvent(ReviewEvent, event_name='review_response_changed'): ...


class ReviewResponseDeletedEvent(ReviewEvent, event_name='review_response_deleted'): ...
