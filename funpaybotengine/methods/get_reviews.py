from __future__ import annotations


__all__ = ['GetReviews']


from funpayparsers.parsers.reviews_parser import ReviewsParser

from funpaybotengine.types import ReviewsBatch
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


class GetReviews(FunPayMethod[ReviewsBatch]):
    """
    Get a sales list (``https://funpay.com/orders/trade``).

    Returns ``funpaybotengine.types.OrderPreviewsBatch`` obj.
    """

    url = 'users/reviews'
    method = HTTPMethod.POST
    data = lambda m, *_: {'user_id': m.user_id, 'continue': m.from_review_id, 'filter': m.filter}
    parser_cls = ReviewsParser
    model_to_build = ReviewsBatch

    user_id: int
    from_review_id: str = ''
    filter: str = ''
