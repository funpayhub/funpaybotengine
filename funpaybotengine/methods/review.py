from __future__ import annotations


__all__ = ('Review',)


from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, model_validator

from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod
from funpaybotengine.exceptions.action_exceptions import ReviewRatingRequiredError


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.client.session.base import RawResponse


class Review(FunPayMethod[bool], BaseModel):
    """
    Leave / edit a review, or reply to one (``https://funpay.com/orders/review``).

    One endpoint, two different acts, and what separates them is who you are on
    the order -- not the URL. As the **buyer** you leave or edit a review, and a
    rating is part of it. As the **seller** you reply, and the site posts
    ``rating=`` empty; the rating on that order is the buyer's and is not yours
    to set.

    ``reply_review`` says which act this is. It exists because the two are
    otherwise indistinguishable at the call site: a reply built with no rating
    would fall back to ``0``, which the site accepts and records as YOUR rating.
    Omitting the rating without saying it is a reply raises
    :class:`~funpaybotengine.exceptions.ReviewRatingRequiredError` at construction,
    before any request goes out.

    Sending a review where one already exists **overwrites** it. There is no
    separate edit call, and none for replying twice.

    Returns ``True``. **The site's answer is not parsed** -- this is not
    evidence of success, only of the absence of an exception.
    """

    order_id: str
    """Reviewing order ID."""

    text: str
    """Review text."""

    rating: Literal[1, 2, 3, 4, 5] | None = None
    """Review rating. ``None`` for a seller's reply.

    ``0`` is gone from the accepted values on purpose: it used to be the way to
    say "no rating", and it was indistinguishable from a real one at every call
    site. Absence is now spelled ``None``, and it is only legal together with
    ``reply_review=True``.
    """

    reply_review: bool = False
    """This is a seller's REPLY, not a review. Sends ``rating=`` empty."""

    def __init__(
        self,
        order_id: str,
        text: str,
        rating: Literal[1, 2, 3, 4, 5] | None = None,
        locale: Language | None = None,
        reply_review: bool = False,
    ):
        super().__init__(
            method=HTTPMethod.POST,
            url='orders/review',
            locale=locale,
            data=make_data,
            headers={'X-Requested-With': 'XMLHttpRequest'},
            order_id=order_id,
            text=text,
            rating=rating,
            reply_review=reply_review,
        )

    @model_validator(mode='after')
    def _rating_matches_the_act(self) -> Review:
        if not self.reply_review and self.rating is None:
            raise ReviewRatingRequiredError(self.order_id)
        return self

    async def parse_result(self, response: RawResponse[Any]) -> bool:
        return True

    async def transform_result(self, parsing_result: Any, response: RawResponse[Any]) -> bool:
        return True


async def make_data(method: Review, bot: Bot) -> dict[str, Any]:
    return {
        'orderId': method.order_id,
        # Empty string, not ``0``: this is the field as the site sends it for a
        # seller's reply, and ``0`` would be a rating.
        'rating': '' if method.rating is None else method.rating,
        'text': method.text,
        'authorId': bot.userid,
    }
