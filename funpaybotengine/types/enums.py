from __future__ import annotations

from enum import Enum, auto

from funpayparsers.types.enums import *  # noqa: F403


class OrderPreviewType(Enum):
    SALE = auto()
    PURCHASE = auto()
    UNKNOWN = auto()


class NoticeChannel(Enum):
    EMAIL = 1
    PUSH = 2
    TELEGRAM = 3
