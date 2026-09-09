from __future__ import annotations


__all__ = ['DeleteReview']


from typing import TYPE_CHECKING, Any

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class DeleteReview(FunPayMethod[bool]):
    """
    Delete a review / reply to review (``https://funpay.com/orders/reviewDelete``).

    Returns ``True``.
    """

    url = 'orders/review'
    method = HTTPMethod.POST
    data = lambda m, bot: {'orderId': m.order_id, 'authorId': bot.userid}
    headers = {'X-Requested-With': 'XMLHttpRequest'}

    order_id: str
    """Reviewing order ID."""

    async def parse_result(self, response: RawResponse[Any]) -> bool:
        return True

    async def transform_result(self, parsing_result: Any, response: RawResponse[Any]) -> bool:
        return True
