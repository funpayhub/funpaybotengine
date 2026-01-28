from __future__ import annotations


__all__ = ['Router']


from typing import cast

from eventry.asyncio.router import Router as BaseRouter

from funpaybotengine.dispatching.handlers.handler_manager import HandlerManager


_events = {
    'chat_changed',
    'new_message',
    'new_sale',
    'sale_closed_by_admin',
    'sale_closed',
    'sale_partially_refunded',
    'sale_refunded',
    'sale_reopened',
    'sale_status_changed',
    'new_purchase',
    'purchase_closed_by_admin',
    'purchase_closed',
    'purchase_partially_refunded',
    'purchase_refunded',
    'purchase_reopened',
    'purchase_status_changed',
    'new_review',
    'review_changed',
    'review_deleted',
    'new_review_response',
    'review_response_changed',
    'review_response_deleted',
    'error',
}


class Router(BaseRouter):
    on_chat_changed: HandlerManager
    on_new_message: HandlerManager
    on_new_sale: HandlerManager
    on_sale_status_changed: HandlerManager
    on_sale_closed: HandlerManager
    on_sale_closed_by_admin: HandlerManager
    on_sale_refunded: HandlerManager
    on_sale_partially_refunded: HandlerManager
    on_sale_reopened: HandlerManager
    on_new_purchase: HandlerManager
    on_purchase_status_changed: HandlerManager
    on_purchase_closed: HandlerManager
    on_purchase_closed_by_admin: HandlerManager
    on_purchase_refunded: HandlerManager
    on_purchase_partially_refunded: HandlerManager
    on_purchase_reopened: HandlerManager
    on_new_review: HandlerManager
    on_review_changed: HandlerManager
    on_review_deleted: HandlerManager
    on_new_review_response: HandlerManager
    on_review_response_changed: HandlerManager
    on_review_response_deleted: HandlerManager
    on_error: HandlerManager

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name=name or f'Router{id(self)}')
        self.set_default_handler_manager(HandlerManager(self, 'default', None))

        for name in _events:
            manager = self._add_handler_manager(HandlerManager(self, f'on_{name}', name))
            setattr(self, f'on_{name}', manager)

    @property
    def on_event(self) -> HandlerManager:
        return cast(HandlerManager, self._default_handler_manager)
