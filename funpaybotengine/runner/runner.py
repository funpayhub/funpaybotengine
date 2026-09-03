from __future__ import annotations


__all__ = [
    'Runner',
    'EventsPack',
]

import time
import asyncio
from typing import TYPE_CHECKING, Any
from dataclasses import field, dataclass
from collections.abc import AsyncGenerator

from funpaybotengine.loggers import runner_logger as logger
from funpaybotengine.exceptions import UnauthorizedError, BotUnauthenticatedError
from funpaybotengine.storage.base import Storage
from funpaybotengine.dispatching.events import BotAuthenticatedEvent, BotUnauthenticatedEvent

from .config import Backoff, RunnerConfig
from ..dispatching import NewEventsPack
from .event_collector import EventCollector


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.dispatching.events import RunnerEvent, BotEngineEvent


events_pack_id = 0


@dataclass
class EventsPack:
    events: list[RunnerEvent[Any] | BotEngineEvent[Any]]
    data: dict[Any, Any] = field(default_factory=dict)
    id: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        global events_pack_id
        if not self.id:
            events_pack_id += 1
            self.id = events_pack_id


class Runner:
    def __init__(
        self,
        bot: Bot,
        *,
        config: RunnerConfig | None = None,
        session_storage: Storage | None = None,
    ) -> None:
        self._bot = bot
        self._config = config
        self._session_storage = session_storage or None

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def config(self) -> RunnerConfig | None:
        return self._config

    @property
    def session_storage(self) -> Storage | None:
        return self._session_storage

    async def listen(
        self,
        config: RunnerConfig | None = None,
        session_storage: Storage | None = None,
    ) -> AsyncGenerator[tuple[RunnerEvent[Any] | BotEngineEvent[Any], EventsPack], None]:
        config = (
            config
            if config is not None
            else self.config
            if self.config is not None
            else RunnerConfig()
        )
        storage = session_storage if session_storage is not None else self._session_storage
        collector = EventCollector(self.bot, config, session_storage=storage)
        backoff = Backoff(config.backoff_config)

        await collector.init_chats()

        while True:
            sleep_time: float | None = None
            start = time.monotonic()
            pack = EventsPack([])

            try:
                pack.events.extend(await collector.get_events())
                if backoff.counter:
                    backoff.reset()
                    logger.info('Connection established. Continuing collecting events.')
                    if config.on_unauthenticated_error_policy == 'event':
                        pack.events.insert(0, BotAuthenticatedEvent(object=None))

            except (BotUnauthenticatedError, UnauthorizedError) as e:
                logger.warning(
                    'Bot is unauthenticated (%s). Executing current policy %r.',
                    e.__class__.__name__,
                    config.on_unauthenticated_error_policy,
                )

                if config.on_unauthenticated_error_policy in ['event', 'ignore']:
                    sleep_time = next(backoff)
                    logger.warning('Current attempt: %d. Delay: %f.', backoff.counter, sleep_time)
                    if backoff.counter == 1 and config.on_unauthenticated_error_policy == 'event':
                        pack.events = [BotUnauthenticatedEvent(object=sleep_time)]

                elif config.on_unauthenticated_error_policy == 'stop':
                    return
            except Exception:
                sleep_time = next(backoff)
                logger.error(
                    'Failed to collect events. Current attempt: %d. Delay: %f.',
                    backoff.counter,
                    sleep_time,
                    exc_info=True,
                )

            if not backoff.counter:
                pack.events.insert(0, NewEventsPack(object=pack.id))

            for i in pack.events:
                yield i, pack

            await _sleep(start, sleep_time if sleep_time else config.interval)


async def _sleep(start_time: int | float, interval: int | float) -> None:
    time_to_sleep = interval - (time.monotonic() - start_time)
    if time_to_sleep > 0:
        await asyncio.sleep(time_to_sleep)
