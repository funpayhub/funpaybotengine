from __future__ import annotations


__all__ = ['HandlerManager']


from typing import Any
from collections.abc import Callable

from eventry.asyncio import HandlerManager as BaseHandlerManager, MiddlewareStorage

from funpaybotengine.dispatching import Event


class HandlerManager(
    BaseHandlerManager[
        Callable[..., Any],
        Callable[..., Any],
        Callable[..., Any],
        Callable[..., Any],
        Callable[..., Any],
    ]
):
    def __init__(self, name: str, event_filter: str | Callable[[Event], bool]) -> None:
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
