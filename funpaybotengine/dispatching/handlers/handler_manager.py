from __future__ import annotations


__all__ = ('HandlerManager',)

from typing import TYPE_CHECKING, cast

from eventry.asyncio.default_types import FilterType, HandlerType, MiddlewareType
from eventry.asyncio.handler_manager import HandlerManager as BaseHandlerManager
from eventry.asyncio.middleware_manager import MiddlewareManager, MiddlewareManagerTypes


if TYPE_CHECKING:
    from funpaybotengine.dispatching.routers import Router


class HandlerManager(BaseHandlerManager[FilterType, HandlerType, MiddlewareType, 'Router']):
    def __init__(
        self,
        router: 'Router',
        name: str,
        event_filter: str | None,
    ):
        super().__init__(
            router=router,
            name=name,
            event_filter=event_filter,
        )

        self._add_middleware_manager(MiddlewareManagerTypes.MANAGER_OUTER, MiddlewareManager())
        self._add_middleware_manager(MiddlewareManagerTypes.MANAGER_INNER, MiddlewareManager())
        self._add_middleware_manager(MiddlewareManagerTypes.HANDLING_PROCESS, MiddlewareManager())
        self._add_middleware_manager(MiddlewareManagerTypes.OUTER_PER_HANDLER, MiddlewareManager())
        self._add_middleware_manager(MiddlewareManagerTypes.INNER_PER_HANDLER, MiddlewareManager())

    @property
    def inner_middleware(self) -> MiddlewareManager:
        return cast(
            MiddlewareManager, self.middleware_manager(MiddlewareManagerTypes.INNER_PER_HANDLER)
        )

    @property
    def outer_middleware(self) -> MiddlewareManager:
        return cast(
            MiddlewareManager, self.middleware_manager(MiddlewareManagerTypes.OUTER_PER_HANDLER)
        )

    @property
    def manager_outer(self) -> MiddlewareManager:
        return cast(
            MiddlewareManager, self.middleware_manager(MiddlewareManagerTypes.MANAGER_OUTER)
        )

    @property
    def manager_inner(self) -> MiddlewareManager:
        return cast(
            MiddlewareManager, self.middleware_manager(MiddlewareManagerTypes.MANAGER_INNER)
        )

    @property
    def handling_process(self) -> MiddlewareManager:
        return cast(
            MiddlewareManager, self.middleware_manager(MiddlewareManagerTypes.HANDLING_PROCESS)
        )
