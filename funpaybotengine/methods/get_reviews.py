from __future__ import annotations


__all__ = ('GetReviews',)


from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from funpayparsers.types import Language
from funpayparsers.parsers import ReviewsParser

from funpaybotengine.types import ReviewsBatch
from funpaybotengine.types.enums import OrderStatus
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


STATE_FILTERS = {
    OrderStatus.COMPLETED: 'closed',
    OrderStatus.PAID: 'paid',
    OrderStatus.REFUNDED: 'refunded',
}


class GetReviews(FunPayMethod[ReviewsBatch], BaseModel):
    """
    Get a sales list (``https://funpay.com/orders/trade``).

    Returns ``funpaybotengine.types.OrderPreviewsBatch`` obj.
    """

    user_id: int
    from_review_id: str
    filter: str

    __model_to_build__ = ReviewsBatch

    def __init__(
        self,
        user_id: int,
        from_review_id: str = '',
        filter: str = '',
        locale: Language | None = None,
    ):
        super().__init__(
            url='users/reviews',
            method=HTTPMethod.POST,
            parser_cls=ReviewsParser,
            data={'user_id': user_id, 'continue': from_review_id, 'filter': filter},
            locale=locale,
            user_id=user_id,
            from_review_id=from_review_id,
            filter=filter,
        )

    async def transform_result(
        self,
        parsing_result: Any,
        response: RawResponse[Any],
    ) -> ReviewsBatch:
        batch = await super().transform_result(parsing_result, response)
        # FunPay omits the hidden ``filter`` and ``user_id`` inputs in some responses,
        # so the scraped values are unreliable. Stamp the ones actually requested to
        # keep the filter (and the profile id needed for pagination) across batches.
        batch.filter = self.filter
        batch.user_id = self.user_id
        return batch
