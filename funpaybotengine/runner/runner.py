from __future__ import annotations


__all__ = ('Runner', 'EventsStack')

import time
import random
import string
import asyncio
from typing import TYPE_CHECKING, Any
from dataclasses import field, dataclass
from collections.abc import Iterator, AsyncGenerator

from funpaybotengine.loggers import runner_logger
from funpaybotengine.exceptions import UnauthorizedError, BotUnauthenticatedError
from funpaybotengine.storage.base import Storage
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.runner.event_collector import EventCollector
from funpaybotengine.dispatching.events.base import RunnerEvent


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot


@dataclass
class EventsStack:
    events: tuple[RunnerEvent[Any], ...]
    data: dict[Any, Any] = field(default_factory=dict)
    id: str = field(init=False, default='')

    def __post_init__(self) -> None:
        self.id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))

    def __getitem__(self, item: Any) -> Any:
        return self.data[item]

    def __setitem__(self, item: Any, value: Any) -> None:
        self.data[item] = value

    def __iter__(self) -> Iterator[RunnerEvent[Any]]:
        return iter(self.events)

    def get(self, value: str, fallback: Any = None) -> Any:
        return self.data.get(value, fallback)


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
    ) -> AsyncGenerator[tuple[RunnerEvent[Any], EventsStack], None]:
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

            events_stack = EventsStack(events=tuple(result))
            for i in events_stack:
                yield i, events_stack

            await _sleep(start, config.interval)


async def _sleep(start_time: int | float, interval: int | float) -> None:
    time_to_sleep = interval - (time.time() - start_time)
    if time_to_sleep > 0:
        await asyncio.sleep(time_to_sleep)
