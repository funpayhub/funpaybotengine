from __future__ import annotations


__all__ = ['Dispatcher']


from typing import Any

from eventry.asyncio import Dispatcher as BaseDispatcher, EventDispatchingConfig
from eventry._execution_context import RouterExecutionContext, HandlerExecutionContext

from funpaybotengine.loggers import dispatcher_logger as logger
from funpaybotengine.dispatching import Router, ExceptionEvent


original_config = EventDispatchingConfig()


async def on_error_callback(ctx: RouterExecutionContext, exc: Exception) -> None:
    if isinstance(ctx.event, ExceptionEvent):
        await original_config.on_error(ctx, exc)
        return

    exc_event = ExceptionEvent(object=exc, context=ctx)

    try:
        await ctx.dispatcher.propagate_event(exc_event)
    except Exception as e:
        logger.error('An error occurred while propagating error event.', exc_info=e)


async def on_handler(ctx: HandlerExecutionContext, result: Any): ...


# todo: do things depends on a type


cfg = EventDispatchingConfig(on_error=on_error_callback, on_handler=on_handler)


class Dispatcher(BaseDispatcher):
    def __init__(self, router: Router | None, context: dict[str, Any] | None = None):
        super().__init__(config=cfg, router=router, event_context=context)
