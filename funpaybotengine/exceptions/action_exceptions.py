from __future__ import annotations


__all__ = ['RefundError', 'RaiseOffersError', 'ReviewRatingRequiredError']
import re

from .base import FunPayBotEngineError


class RefundError(FunPayBotEngineError):
    def __init__(self, order_id: str, message: str):
        super().__init__()
        self.order_id = order_id
        self.message = message

    def __str__(self) -> str:
        return self.message


class ReviewRatingRequiredError(FunPayBotEngineError):
    """Leaving a review needs a rating; replying to one does not.

    orders/review serves both, and what separates them is not the endpoint
    but who you are on the order: as the buyer you rate, as the seller you
    reply, and the site posts rating= empty.

    Raised at construction, before any request. Without it the two collapse
    into one: a reply built with no rating would post rating=0, which the
    site accepts and records as the sender's rating on that order.
    """

    def __init__(self, order_id: str) -> None:
        super().__init__()
        self.order_id = order_id

    def __str__(self) -> str:
        return (
            f'{self.order_id}: rating is required to leave a review; '
            f'to reply to one as the seller pass reply_review=True'
        )


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
