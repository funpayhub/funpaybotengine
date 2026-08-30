from __future__ import annotations


__all__ = ('Refund',)


import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from funpaybotengine.loggers import methods_logger
from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod
from funpaybotengine.exceptions.action_exceptions import RefundError


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


_LOG_BODY_LIMIT = 500
"""How much of an unparsable body reaches the log.

The whole thing would be the obvious choice and is the wrong one: when the
answer is a login page it is a full HTML document, and every failed refund would
put one in the log. The head is what identifies it; the length is printed beside
it so nothing is silently hidden.
"""


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
        except json.JSONDecodeError as exc:
            # The raw body only at DEBUG: it is the one thing that says WHY this
            # did not parse, and it is also a whole page of HTML when the answer
            # was a login form.
            methods_logger.debug(
                'refund %s: response is not JSON (%d bytes): %r%s',
                self.order_id,
                len(response.raw_response),
                response.raw_response[:_LOG_BODY_LIMIT],
                '...' if len(response.raw_response) > _LOG_BODY_LIMIT else '',
            )
            raise RefundError(
                order_id=self.order_id,
                message=f'Unable to refund order {self.order_id}: {exc}',
            ) from exc

        if result.get('error'):
            raise RefundError(
                order_id=self.order_id,
                message=result.get('msg') or f'Unable to refund order {self.order_id}',
            )
        return True

    async def transform_result(self, parsing_result: Any, response: RawResponse[Any]) -> bool:
        return True
