from __future__ import annotations


__all__ = ('RunnerConfig', 'BackoffConfig', 'Backoff')


import asyncio
from typing import Literal
from dataclasses import dataclass


@dataclass(frozen=True)
class BackoffConfig:
    min_delay: float = 6.0
    max_delay: float = 18.0
    factor: float = 1.3

    def __post_init__(self) -> None:
        if self.max_delay <= self.min_delay:
            raise ValueError('`max_delay` must be greater than `min_delay`.')
        if self.factor <= 1:
            raise ValueError('`factor` must be greater than 1')


@dataclass
class RunnerConfig:
    interval: int | float = 4.0
    """
    Interval between updates requests.
    Must be more than ``0``.
    
    Defaults to ``4.0``.
    """

    discover_sales: bool = True
    """Whether to discover new sales or not."""

    discover_purchases: bool = True
    """Whether to discover new purchases or not."""

    keep_unread: bool = False
    """
    Whether to preserve the unread status of chats when getting updates.

    If ``False`` (default), a batch method is used: up to 10 chats can be requested in a single
    request, but they will be marked as read.

    If ``True``, only one chat can be fetched per request to keep it unread.  
    With high incoming message volume this leads to many requests and may cause
    ``429 Too Many Requests`` errors.
    """

    on_unauthenticated_error_policy: Literal['ignore', 'event', 'stop'] = 'ignore'
    """
    What to do when an `BotUnauthenticatedError` occurred during fetching updates process?
    
    - ``ignore``: ignore the error and continue fetching updates.
    - ``event``: yield an error event and continue fetching updates.
    - ``stop``: stop fetching updates, exit a function.
    
    Defaults to ``ignore``.
    """

    backoff_config: BackoffConfig = BackoffConfig()

    def __post_init__(self) -> None:
        if self.interval < 0:
            raise ValueError('`interval` must be greater than 0.')


class Backoff:
    def __init__(self, config: BackoffConfig) -> None:
        self.config = config
        self._next_delay = config.min_delay
        self._current_delay = 0.0
        self._counter = 0

    def __iter__(self) -> Backoff:
        return self

    @property
    def min_delay(self) -> float:
        return self.config.min_delay

    @property
    def max_delay(self) -> float:
        return self.config.max_delay

    @property
    def factor(self) -> float:
        return self.config.factor

    @property
    def next_delay(self) -> float:
        return self._next_delay

    @property
    def current_delay(self) -> float:
        return self._current_delay

    @property
    def counter(self) -> int:
        return self._counter

    async def asleep(self) -> None:
        await asyncio.sleep(next(self))

    def _calculate_next(self, value: float) -> float:
        return min(value * self.factor, self.max_delay)

    def __next__(self) -> float:
        self._current_delay = self._next_delay
        self._next_delay = self._calculate_next(self._next_delay)
        self._counter += 1
        return self._current_delay

    def reset(self) -> None:
        self._current_delay = 0.0
        self._counter = 0
        self._next_delay = self.min_delay
