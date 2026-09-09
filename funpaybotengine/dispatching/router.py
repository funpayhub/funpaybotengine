from __future__ import annotations


__all__ = ['Router']

from typing import Any
from collections.abc import Callable

from eventry.asyncio.router import Router as BaseRouter

from funpaybotengine.dispatching import events
from funpaybotengine.dispatching.handler_manager import HandlerManager


class Router(BaseRouter[Callable[..., Any]]):
    def __init__(self, name: str = '') -> None:
        super().__init__(name=name or f'Router{id(self)}')

        self.on_chat_changed = self._fpbe_mgr(events.ChatChanged)
        self.on_new_message = self._fpbe_mgr(events.NewMessage, True)
        self.on_new_sale = self._fpbe_mgr(events.NewSale)
        self.on_sale_status_changed = self._fpbe_mgr(events.SaleStatusChanged, True)
        self.on_sale_closed = self._fpbe_mgr(events.SaleClosed)
        self.on_sale_closed_by_admin = self._fpbe_mgr(events.SaleClosedByAdmin)
        self.on_sale_refunded = self._fpbe_mgr(events.SaleRefunded)
        self.on_sale_partially_refunded = self._fpbe_mgr(events.SalePartiallyRefunded)
        self.on_sale_reopened = self._fpbe_mgr(events.SaleReopened)
        self.on_new_purchase = self._fpbe_mgr(events.NewPurchase)
        self.on_purchase_status_changed = self._fpbe_mgr(events.PurchaseStatusChanged, True)
        self.on_purchase_closed = self._fpbe_mgr(events.PurchaseClosed)
        self.on_purchase_closed_by_admin = self._fpbe_mgr(events.PurchaseClosedByAdmin)
        self.on_purchase_refunded = self._fpbe_mgr(events.PurchaseRefunded)
        self.on_purchase_partially_refunded = self._fpbe_mgr(events.PurchasePartiallyRefunded)
        self.on_purchase_reopened = self._fpbe_mgr(events.PurchaseReopened)
        self.on_new_review = self._fpbe_mgr(events.NewReview)
        self.on_review_changed = self._fpbe_mgr(events.ReviewChanged)
        self.on_review_deleted = self._fpbe_mgr(events.ReviewDeleted)
        self.on_new_review_response = self._fpbe_mgr(events.NewReviewReply)
        self.on_review_response_changed = self._fpbe_mgr(events.ReviewReplyChanged)
        self.on_review_response_deleted = self._fpbe_mgr(events.ReviewReplyDeleted)
        self.on_error = self._fpbe_mgr(events.ExceptionEvent, True)
        self.on_unauthenticated = self._fpbe_mgr(events.BotUnauthenticatedEvent)
        self.on_authenticated = self._fpbe_mgr(events.BotAuthenticatedEvent)
        self.on_new_events_pack = self._fpbe_mgr(events.NewEventsPack)

    def _fpbe_mgr(
        self, event: type[events.Event[Any]], instance_check: bool = False
    ) -> HandlerManager:
        manager = HandlerManager(
            f'on_{event.__event_name__}',
            (lambda e: isinstance(e, event)) if instance_check else event.__event_name__,
        )
        return self.add_handler_manager(manager)
