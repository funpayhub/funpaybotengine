from __future__ import annotations


__all__ = ['HandlerManager']


from eventry.asyncio import HandlerManager as BaseHandlerManager
from eventry.asyncio.middleware_manager import MiddlewareStorage


class HandlerManager(BaseHandlerManager):
    def __init__(self, name: str, event_filter: str | None) -> None:
        super().__init__(name=name, event_filter=event_filter)

        self.middleware.set_middlewares_storage('manager.outer', MiddlewareStorage())
        self.middleware.set_middlewares_storage('manager.inner', MiddlewareStorage())
        self.middleware.set_middlewares_storage('handler.outer', MiddlewareStorage())
        self.middleware.set_middlewares_storage('handler.inner', MiddlewareStorage())

    @property
    def manager_outer_middleware(self) -> MiddlewareStorage:
        return self.middleware.get_middlewares_storage('manager.outer')

    @property
    def manager_inner_middleware(self) -> MiddlewareStorage:
        return self.middleware.get_middlewares_storage('manager.inner')

    @property
    def handler_outer_middleware(self) -> MiddlewareStorage:
        return self.middleware.get_middlewares_storage('handler.outer')

    @property
    def handler_inner_middleware(self) -> MiddlewareStorage:
        return self.middleware.get_middlewares_storage('handler.inner')
