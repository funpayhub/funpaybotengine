from __future__ import annotations


__all__ = ['HandlerManager']


from typing import Any
from collections.abc import Callable

from eventry.asyncio import HandlerManager as BaseHandlerManager, MiddlewareStorage
from eventry.asyncio.event import Event
from eventry.asyncio.config import Context, FromContext, HandlerManagerConfig


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

        self.middleware['manager.outer'] = MiddlewareStorage()
        self.middleware['manager.inner'] = MiddlewareStorage()
        self.middleware['handler.outer'] = MiddlewareStorage()
        self.middleware['handler.inner'] = MiddlewareStorage()
        self._config = HandlerManagerConfig(
            manager_outer_mdw_args=(FromContext('next_call'), Context),
            manager_inner_mdw_args=(FromContext('next_call'), Context),
            handler_outer_mdw_args=(FromContext('next_call'), Context),
            handler_inner_mdw_args=(FromContext('next_call'), Context),
        )

    @property
    def manager_outer_middleware(self) -> MiddlewareStorage:
        return self.middleware['manager.outer']

    @property
    def manager_inner_middleware(self) -> MiddlewareStorage:
        return self.middleware['manager.inner']

    @property
    def handler_outer_middleware(self) -> MiddlewareStorage:
        return self.middleware['handler.outer']

    @property
    def handler_inner_middleware(self) -> MiddlewareStorage:
        return self.middleware['handler.inner']
