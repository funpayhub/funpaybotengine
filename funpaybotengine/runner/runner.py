from __future__ import annotations


__all__ = ('Runner', 'EventsPack')

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
from funpaybotengine.dispatching.events import BotAuthenticatedEvent, BotUnauthenticatedEvent

from .config import Backoff, RunnerConfig
from ..dispatching import NewEventsPack
from .event_collector import EventCollector


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.dispatching.events import RunnerEvent, BotEngineEvent


@dataclass
class EventsPack:
    events: tuple[RunnerEvent[Any] | BotEngineEvent[Any], ...]
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
    ) -> AsyncGenerator[tuple[RunnerEvent[Any], EventsPack], None]:
        config = config or RunnerConfig()
        collector = EventCollector(
            self.bot,
            config,
            session_storage=session_storage,
        )
        backoff = Backoff(config.backoff_config)

        await collector.init_chats()

        sleep_time: float | None = None
        while True:
            start = time.time()
            result: list[RunnerEvent[Any] | BotEngineEvent[Any]] = []

            try:
                result = await collector.get_events()
                if backoff.counter:
                    backoff.reset()
                    runner_logger.info('Connection established. Continuing collecting events.')
                    if config.on_unauthenticated_error_policy == 'event':
                        result.insert(0, BotAuthenticatedEvent(object=None))

            except (BotUnauthenticatedError, UnauthorizedError) as e:
                runner_logger.warning(
                    'Bot is unauthenticated (%s). Executing current policy %r.',
                    e.__class__.__name__,
                    config.on_unauthenticated_error_policy,
                )

                if config.on_unauthenticated_error_policy in ['event', 'ignore']:
                    next(backoff)
                    sleep_time = backoff.current_delay
                    runner_logger.warning(
                        'Current attempt: %d. Delay: %f.', backoff.counter, backoff.current_delay
                    )
                    if backoff.counter == 1 and config.on_unauthenticated_error_policy == 'event':
                        result = [
                            BotUnauthenticatedEvent(object=None, delay=backoff.current_delay)
                        ]

                elif config.on_unauthenticated_error_policy == 'stop':
                    return
            except Exception:
                next(backoff)
                runner_logger.error(
                    'Failed to collect events. Current attempt: %d. Delay: %f.',
                    backoff.counter,
                    backoff.current_delay,
                    exc_info=True,
                )
                sleep_time = backoff.current_delay

            events_stack = EventsPack(events=())
            if not backoff.counter:
                result.insert(0, NewEventsPack(object=events_stack.id))
            events_stack.events = tuple(result)

            for i in events_stack:
                yield i, events_stack

            if sleep_time:
                await asyncio.sleep(sleep_time)
                sleep_time = None
            else:
                await _sleep(start, config.interval)


async def _sleep(start_time: int | float, interval: int | float) -> None:
    time_to_sleep = interval - (time.time() - start_time)
    if time_to_sleep > 0:
        await asyncio.sleep(time_to_sleep)
