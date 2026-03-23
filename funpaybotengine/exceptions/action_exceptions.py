from __future__ import annotations


__all__ = ['RefundError', 'RaiseOffersError']
import re

from .base import FunPayBotEngineError


class RefundError(FunPayBotEngineError):
    def __init__(self, order_id: str, message: str):
        super().__init__()
        self.order_id = order_id
        self.message = message

    def __str__(self) -> str:
        return self.message


class RaiseOffersError(FunPayBotEngineError):
    def __init__(
        self,
        response: str,
        category_id: int,
        message: str | None,
    ) -> None:
        super().__init__()
        self.raw_response = response
        self.category_id = category_id
        self.message = message

    @staticmethod
    def parse_wait_time(response: str) -> int:
        x = re.search(r'(\d+)\s+', response)
        time = int(x.group(1)) if x else 0

        if 'секунд' in response or 'second' in response:
            return time or 2
        if 'минут' in response or 'хвилин' in response or 'minute' in response:
            return (time or 1) * 60
        if 'час' in response or 'годин' in response or 'hour' in response:
            return (time or 1) * 3600

        return 10

    @property
    def wait_time(self) -> int:
        return self.parse_wait_time(self.message or '')
