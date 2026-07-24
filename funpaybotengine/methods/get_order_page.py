from __future__ import annotations


__all__ = ['GetOrderPage']


from funpayparsers.parsers.page_parsers import OrderPageParser

from funpaybotengine.types.pages import OrderPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetOrderPage(FunPayMethod[OrderPage]):
    """
    Get an order page method (``https://funpay.com/orders/<order_id>/``).

    Returns ``funpaybotengine.types.pages.OrderPage`` obj.
    """
    url = lambda m, *_: f'orders/{m.order_id}/'
    method = HTTPMethod.GET
    parser_cls = OrderPageParser
    model_to_build__ = OrderPage

    order_id: str
    """Order ID."""
