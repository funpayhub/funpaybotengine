from __future__ import annotations


__all__ = ['GetReviews']


from funpayparsers.parsers.reviews_parser import ReviewsParser

from funpaybotengine.types import ReviewsBatch
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


class GetReviews(FunPayMethod[ReviewsBatch]):
    """
    Get a reviews list of a user (``https://funpay.com/users/reviews``).

    Returns ``funpaybotengine.types.ReviewsBatch`` obj.
    """

    url = 'users/reviews'
    method = HTTPMethod.POST
    data = lambda m, *_: {'user_id': m.user_id, 'continue': m.from_review_id, 'filter': m.filter}
    context = lambda m, *_: {'reviews_user_id': m.user_id, 'reviews_filter': m.filter}
    parser_cls = ReviewsParser
    model_to_build = ReviewsBatch

    user_id: int
    from_review_id: str = ''
    filter: str = ''
