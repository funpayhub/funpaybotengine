from __future__ import annotations


__all__ = ['Refund']


import json
from typing import TYPE_CHECKING, Any

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod
from funpaybotengine.exceptions.action_exceptions import RefundError


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class Refund(FunPayMethod[bool]):
    """
    Refund an order (``https://funpay.com/orders/refund``).

    Returns ``True``.
    """

    url = 'orders/refund'
    method = HTTPMethod.POST
    data = lambda m, *_: {'id': m.order_id}
    headers = {'X-Requested-With': 'XMLHttpRequest'}

    order_id: str
    """Order ID to refund."""

    async def parse_result(self, response: RawResponse[Any]) -> bool:
        try:
            result = json.loads(response.raw_response)
        except:
            raise RefundError(self.order_id, f'Unable to refund order {self.order_id}')

        if result.get('error'):
            raise RefundError(self.order_id, result.get('msg') or f'Unable to refund order {self.order_id}')
        return True

    async def transform_result(self, parsing_result: Any, response: RawResponse[Any]) -> bool:
        return True
