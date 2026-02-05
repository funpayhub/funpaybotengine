from __future__ import annotations

from enum import Enum, auto

from funpayparsers.types.enums import *  # noqa: F403


class TransactionFilter(str, Enum):
    """
    Transaction list filter values for ``users/transactions``.

    - ``ALL`` (``''``): no filter;
    - ``PAYMENT``: payment transactions;
    - ``WITHDRAW``: withdrawal transactions;
    - ``ORDER``: order-related transactions;
    - ``OTHER``: other transaction types;
    """

    ALL = ''
    """All transactions."""

    PAYMENT = 'payment'
    """Payment transactions."""

    WITHDRAW = 'withdraw'
    """Withdrawal transactions."""

    ORDER = 'order'
    """Order-related transactions."""

    OTHER = 'other'
    """Other transactions."""


class OrderPreviewType(Enum):
    SALE = auto()
    PURCHASE = auto()
    UNKNOWN = auto()


class NoticeChannel(Enum):
    EMAIL = 1
    PUSH = 2
    TELEGRAM = 3
