from __future__ import annotations


__all__ = [
    'ChatInitEvent',
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

from .base import RunnerEvent
from ...types.pages import OrderPage


class ChatInitEvent(RunnerEvent[PrivateChatPreview]):
    @property
    def chat_preview(self) -> PrivateChatPreview:
        return self.object

    @property
    def event_context_injection(self) -> dict[str, Any]:
        return {
            'chat_preview': self.chat_preview,
        }


class ChatChangedEvent(RunnerEvent[PrivateChatPreview]):
    previous: PrivateChatPreview | None = None

    @property
    def chat_preview(self) -> PrivateChatPreview:
        return self.object

    @property
    def event_context_injection(self) -> dict[str, Any]:
        return {
            'chat_preview': self.chat_preview,
        }


class NewMessageEvent(RunnerEvent[Message]):
    @property
    def message(self) -> Message:
        return self.object

    @property
    def event_context_injection(self) -> dict[str, Any]:
        return {
            'message': self.message,
        }


class FromMessageEvent(NewMessageEvent):
    related_new_message_event: NewMessageEvent

    @property
    def event_context_injection(self) -> dict[str, Any]:
        val = super().event_context_injection
        val.update({'new_message_event': self.related_new_message_event})
        return val


class OrderEvent(RunnerEvent[Message]):
    _order_preview: OrderPreview | None = PrivateAttr(default=None)

    async def get_order_preview(self, update: bool = False) -> OrderPreview:
        raise NotImplementedError


class SaleEvent(OrderEvent):
    async def get_order_preview(self, update: bool = False) -> OrderPreview:
        if self._order_preview is not None and not update:
            return self._order_preview

        orders = await self.get_bound_bot().get_sales(order_id_filter=self.object.meta.order_id)
        return orders.orders[0]


class PurchaseEvent(OrderEvent):
    async def get_order_preview(self, update: bool = False) -> OrderPreview:
        if self._order_preview is not None and not update:
            return self._order_preview

        orders = await self.get_bound_bot().get_purchases(
            order_id_filter=self.object.meta.order_id,
        )
        return orders.orders[0]


class NewSaleEvent(SaleEvent):
    related_auto_message_events: list[NewMessageEvent] = Field(default_factory=list)


class SaleStatusChangedEvent(SaleEvent):
    previous: OrderPreview | None = None


class SaleClosedEvent(SaleStatusChangedEvent): ...


class SaleClosedByAdminEvent(SaleClosedEvent): ...


class SaleRefundedEvent(SaleStatusChangedEvent): ...


class SalePartiallyRefundedEvent(SaleRefundedEvent): ...


class SaleReopenedEvent(SaleStatusChangedEvent): ...


class NewPurchaseEvent(PurchaseEvent):
    related_auto_message_events: list[NewMessageEvent] = Field(default_factory=list)


class PurchaseStatusChangedEvent(PurchaseEvent):
    previous: OrderPreview | None = None


class PurchaseClosedEvent(PurchaseStatusChangedEvent): ...


class PurchaseClosedByAdminEvent(PurchaseClosedEvent): ...


class PurchaseRefundedEvent(PurchaseStatusChangedEvent): ...


class PurchasePartiallyRefundedEvent(PurchaseRefundedEvent): ...


class PurchaseReopenedEvent(PurchaseStatusChangedEvent): ...


class ReviewEvent(FromMessageEvent):
    _order_page: OrderPage | None = PrivateAttr(default=None)

    async def get_order_page(self, update: bool = False) -> OrderPage:
        if self._order_page is None or update:
            bot = self.get_bound_bot()
            self._order_page = await bot.get_order_page(self.object.meta.order_id or '')

        return self._order_page

    async def get_review(self, update: bool = False) -> Review | None:
        order_page = await self.get_order_page(update)
        return order_page.review


class NewReviewEvent(ReviewEvent): ...


class ReviewChangedEvent(ReviewEvent): ...


class ReviewDeletedEvent(ReviewEvent): ...


class NewReviewResponseEvent(ReviewEvent): ...


class ReviewResponseChangedEvent(ReviewEvent): ...


class ReviewResponseDeletedEvent(ReviewEvent): ...
