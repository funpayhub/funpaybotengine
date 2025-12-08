from __future__ import annotations


__all__ = ('RunnerConfig',)


from typing import Literal
from dataclasses import dataclass


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

    on_unauthenticated_error_policy: Literal['ignore', 'event', 'stop', 'stop+event'] = 'ignore'
    """
    What to do when an `BotUnauthenticatedError` occurred during fetching updates process?
    
    - ``ignore``: ignore the error and continue fetching updates.
    - ``event``: yield an error event and continue fetching updates.
    - ``stop``: stop fetching updates, exit a function.
    - ``stop+event``: yield an error event and stop fetching updates, exit a function.
    
    Defaults to ``ignore``.
    """
