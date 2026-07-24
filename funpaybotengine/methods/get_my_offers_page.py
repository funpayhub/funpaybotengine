from __future__ import annotations


__all__ = ['GetMyOffersPage']

from funpayparsers.parsers.page_parsers import MyOffersPageParser

from funpaybotengine.types.pages import MyOffersPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


class GetMyOffersPage(FunPayMethod[MyOffersPage]):
    """
    Get personal lots page (``https://funpay.com/lots/<subcategory_id>/trade``).

    Returns ``funpaybotengine.types.pages.MyOffersPage``.
    """
    url = lambda m, *_: f'lots/{m.subcategory_id}/trade'
    method = HTTPMethod.GET
    parser_class = MyOffersPageParser
    model_to_build_class = MyOffersPage

    subcategory_id: int
    """Subcategory ID."""
