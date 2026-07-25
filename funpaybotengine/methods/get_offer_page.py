from __future__ import annotations


__all__ = ['GetOfferPage']


from funpayparsers.parsers.page_parsers import OfferPageParser

from funpaybotengine.types.pages import OfferPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetOfferPage(FunPayMethod[OfferPage]):
    """
    Get an order page method (``https://funpay.com/<lots/chips>/offer?id=<offer_id>``).

    Returns ``funpaybotengine.types.pages.OfferPage`` obj.
    """

    url = lambda m, *_: ("lots" if isinstance(m.offer_id, int) else "chips") + '/offer'
    method = HTTPMethod.GET
    data = lambda m, *_: {'id': str(m.offer_id)}
    allow_anonymous = True
    allow_uninitialized = True
    parser_cls = OfferPageParser
    model_to_build = OfferPage

    offer_id: int | str
