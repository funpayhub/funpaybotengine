from __future__ import annotations


__all__ = ['GetReviews']


from typing import TYPE_CHECKING, Any

from funpayparsers.types.reviews import ReviewsBatch as ParsedReviewsBatch
from funpayparsers.parsers.reviews_parser import ReviewsParser

from funpaybotengine.types import ReviewsBatch
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import RawResponse


class GetReviews(FunPayMethod[ReviewsBatch]):
    """
    Get a reviews list of a user (``https://funpay.com/users/reviews``).

    Returns ``funpaybotengine.types.ReviewsBatch`` obj.
    """

    url = 'users/reviews'
    method = HTTPMethod.POST
    data = lambda m, *_: {'user_id': m.user_id, 'continue': m.from_review_id, 'filter': m.filter}
    parser_cls = ReviewsParser
    model_to_build = ReviewsBatch

    user_id: int
    from_review_id: str = ''
    filter: str = ''

    async def parse_result(self, response: RawResponse[Any]) -> ParsedReviewsBatch:
        result: ParsedReviewsBatch = await super().parse_result(response)

        # FunPay omits the hidden ``user_id`` / ``filter`` inputs in a part of the
        # ``users/reviews`` responses, so the parsed values are unreliable. The requested
        # ones are known here and are what the next batch has to be asked with.
        result.user_id = self.user_id
        result.filter = self.filter
        return result
