from __future__ import annotations


__all__ = ('Runner',)


import time
import asyncio
from typing import TYPE_CHECKING, Any
from collections.abc import AsyncGenerator

from funpaybotengine.loggers import runner_logger
from funpaybotengine.exceptions import UnauthorizedError, BotUnauthenticatedError
from funpaybotengine.storage.base import Storage
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.runner.event_collector import EventCollector
from funpaybotengine.dispatching.events.base import RunnerEvent


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot


class Runner:
    def __init__(self, bot: Bot):
        self._bot = bot

    @property
    def bot(self) -> Bot:
        return self._bot

    async def listen(
        self,
        config: RunnerConfig | None = None,
        session_storage: Storage | None = None,
    ) -> AsyncGenerator[tuple[RunnerEvent[Any], tuple[RunnerEvent[Any], ...]]]:
        config = config or RunnerConfig()
        collector = EventCollector(
            self.bot,
            config,
            session_storage=session_storage,
        )

        await collector.init_chats()

        while True:
            start = time.time()

            try:
                result = await collector.get_events()
            except (BotUnauthenticatedError, UnauthorizedError) as e:
                runner_logger.warning(
                    'Bot is unauthenticated (%s). Executing current policy %r.',
                    e.__class__.__name__,
                    config.on_unauthenticated_error_policy,
                )
                if config.on_unauthenticated_error_policy == 'event':
                    ...
                elif config.on_unauthenticated_error_policy == 'stop':
                    return
                elif config.on_unauthenticated_error_policy == 'stop+event':
                    return  # todo yield event
                await _sleep(start, config.interval)
                continue

            events_stack = tuple(result)
            for i in events_stack:
                yield i, events_stack

            await _sleep(start, config.interval)


async def _sleep(start_time: int | float, interval: int | float):
    time_to_sleep = interval - (time.time() - start_time)
    if time_to_sleep > 0:
        await asyncio.sleep(time_to_sleep)
