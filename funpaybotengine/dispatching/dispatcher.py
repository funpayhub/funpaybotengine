from __future__ import annotations


__all__ = ['Dispatcher']


from typing import Any

from eventry.asyncio import (
    Dispatcher as BaseDispatcher,
    DispatchingContext,
    EventDispatchingConfig,
    default_error_callback,
)

from funpaybotengine.loggers import dispatcher_logger as logger
from funpaybotengine.dispatching import Router, ExceptionEvent


async def on_error_callback(ctx: DispatchingContext, exc: Exception) -> None:
    if isinstance(ctx.event, ExceptionEvent):
        await default_error_callback(ctx, exc)
        return

    exc_event = ExceptionEvent(object=exc, context=ctx)

    try:
        await ctx.dispatcher.propagate_event(exc_event)
    except Exception as e:
        logger.error('An error occurred while propagating error event.', exc_info=e)


async def on_handler(ctx: DispatchingContext, result: Any) -> None: ...


# todo: do things depends on a type


class Dispatcher(BaseDispatcher):
    def __init__(
        self,
        router: Router | None = None,
        context: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            config=EventDispatchingConfig(on_error=on_error_callback, on_handler=on_handler),
            router=router,
            event_context=context,
        )
