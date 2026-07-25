from __future__ import annotations


__all__ = ['GetMyChipsPage']

from funpayparsers.parsers.page_parsers import MyChipsPageParser

from funpaybotengine.types.pages import MyChipsPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


class GetMyChipsPage(FunPayMethod[MyChipsPage]):
    """
    Get personal chips page (``https://funpay.com/chips/<subcategory_id>/trade``).

    Returns ``funpaybotengine.types.pages.MyChipsPage``.
    """

    url = lambda m, *_: f'chips/{m.subcategory_id}/trade'
    method = HTTPMethod.GET
    parser_cls = MyChipsPageParser
    model_to_build = MyChipsPage

    subcategory_id: int
    """Subcategory ID."""
