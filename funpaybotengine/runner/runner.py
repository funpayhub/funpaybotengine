from __future__ import annotations


__all__ = ('Runner',)


import time
import asyncio
from typing import TYPE_CHECKING, Any
from collections.abc import AsyncGenerator

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
            result = await collector.get_events()

            events_stack = tuple(result)
            for i in events_stack:
                yield i, events_stack

            time_to_sleep = config.interval - (time.time() - start)
            if time_to_sleep > 0:
                await asyncio.sleep(time_to_sleep)
