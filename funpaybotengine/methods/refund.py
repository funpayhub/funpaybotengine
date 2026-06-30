from __future__ import annotations


__all__ = ('Refund',)


import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod
from funpaybotengine.exceptions.action_exceptions import RefundError


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class Refund(FunPayMethod[bool], BaseModel):
    """
    Refund an order (``https://funpay.com/orders/refund``).

    Returns ``True``.
    """

    order_id: str
    """Order ID to refund."""

    def __init__(self, order_id: str, locale: Language | None = None):
        super().__init__(
            method=HTTPMethod.POST,
            url='orders/refund',
            locale=locale,
            data={'id': order_id},
            headers={'X-Requested-With': 'XMLHttpRequest'},
            order_id=order_id,
        )

    async def parse_result(self, response: RawResponse[Any]) -> bool:
        try:
            result = json.loads(response.raw_response)
        except json.decoder.JSONDecodeError:
            raise RefundError(
                order_id=self.order_id,
                message=f'Unable to refund order {self.order_id}',
            ) from None

        if result.get('error'):
            raise RefundError(
                order_id=self.order_id,
                message=result.get('msg') or f'Unable to refund order {self.order_id}',
            )
        return True

    async def transform_result(self, parsing_result: Any, response: RawResponse[Any]) -> bool:
        return True
