from __future__ import annotations


__all__ = ['Router']


from eventry.asyncio.router import Router as BaseRouter

from funpaybotengine.dispatching import HandlerManager, events


class Router(BaseRouter):
    def __init__(self, name: str = '') -> None:
        super().__init__(name=name or f'Router{id(self)}')

        self.on_chat_changed = self._fpbe_mgr(events.ChatChangedEvent)
        self.on_new_message = self._fpbe_mgr(events.NewMessageEvent)
        self.on_new_sale = self._fpbe_mgr(events.NewSaleEvent)
        self.on_sale_status_changed = self._fpbe_mgr(events.SaleStatusChangedEvent, True)
        self.on_sale_closed = self._fpbe_mgr(events.SaleClosedEvent)
        self.on_sale_closed_by_admin = self._fpbe_mgr(events.SaleClosedByAdminEvent)
        self.on_sale_refunded = self._fpbe_mgr(events.SaleRefundedEvent)
        self.on_sale_partially_refunded = self._fpbe_mgr(events.SalePartiallyRefundedEvent)
        self.on_sale_reopened = self._fpbe_mgr(events.SaleReopenedEvent)
        self.on_new_purchase = self._fpbe_mgr(events.NewPurchaseEvent)
        self.on_purchase_status_changed = self._fpbe_mgr(events.PurchaseStatusChangedEvent, True)
        self.on_purchase_closed = self._fpbe_mgr(events.PurchaseClosedEvent)
        self.on_purchase_closed_by_admin = self._fpbe_mgr(events.PurchaseClosedByAdminEvent)
        self.on_purchase_refunded = self._fpbe_mgr(events.PurchaseRefundedEvent)
        self.on_purchase_partially_refunded = self._fpbe_mgr(events.PurchasePartiallyRefundedEvent)
        self.on_purchase_reopened = self._fpbe_mgr(events.PurchaseReopenedEvent)
        self.on_new_review = self._fpbe_mgr(events.NewReviewEvent)
        self.on_review_changed = self._fpbe_mgr(events.ReviewChangedEvent)
        self.on_review_deleted = self._fpbe_mgr(events.ReviewDeletedEvent)
        self.on_new_review_response = self._fpbe_mgr(events.NewReviewResponseEvent)
        self.on_review_response_changed = self._fpbe_mgr(events.ReviewResponseChangedEvent)
        self.on_error = self._fpbe_mgr(events.ExceptionEvent, True)
        self.on_unauthenticated = self._fpbe_mgr(events.BotUnauthenticatedEvent)
        self.on_authenticated = self._fpbe_mgr(events.BotAuthenticatedEvent)
        self.on_new_events_pack = self._fpbe_mgr(events.NewEventsPack)

    def _fpbe_mgr(self, event: type[events.Event], instance_check: bool = False) -> HandlerManager:
        manager = HandlerManager(
            f'on_{event.__event_name__}',
            (lambda e: isinstance(e, event)) if instance_check else event.__event_name__,
        )
        return self.add_handler_manager(manager)
