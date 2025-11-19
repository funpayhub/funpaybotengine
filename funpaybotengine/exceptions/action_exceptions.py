from __future__ import annotations


__all__ = ['RefundError', 'RaiseOffersError']
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
        wait_time: int | None,
    ) -> None:
        super().__init__()
        self.raw_response = response
        self.category_id = category_id
        self.message = message
        self.wait_time = wait_time
