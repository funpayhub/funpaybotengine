"""`orders/review` serves two different acts; the tests keep them apart.

As the buyer you leave or edit a review and a rating is part of it. As the
seller you reply, and the site posts ``rating=`` empty -- the rating on that
order is the buyer's.

The expected reply body is not invented: it is the form captured from the
site's own request when a seller replies.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError
from funpaybotengine.exceptions import ReviewRatingRequiredError
from funpaybotengine.methods.review import Review


class _Bot:
    userid = 8331834


async def body(method: Review) -> dict[str, Any]:
    return await method.data(method, _Bot())  # type: ignore[arg-type,no-any-return]


@pytest.mark.asyncio
async def test_a_seller_reply_sends_an_empty_rating() -> None:
    assert await body(Review(order_id='JDPEUYUS', text='thanks', reply_review=True)) == {
        'orderId': 'JDPEUYUS',
        'rating': '',
        'text': 'thanks',
        'authorId': 8331834,
    }


@pytest.mark.asyncio
async def test_a_review_still_carries_its_rating() -> None:
    assert (await body(Review(order_id='X', text='t', rating=5)))['rating'] == 5


def test_omitting_the_rating_without_saying_it_is_a_reply_is_refused() -> None:
    """The whole point of the flag.

    Without it a reply is built with no rating, falls back to ``0``, and the
    site records that as the sender's rating on the order. Nothing raises, and
    it is visible only on the order page afterwards.
    """
    with pytest.raises(ReviewRatingRequiredError) as caught:
        Review(order_id='X', text='t')
    assert caught.value.order_id == 'X'


def test_zero_is_no_longer_a_way_to_say_no_rating() -> None:
    """It used to be, and at a call site it read as a real rating."""
    with pytest.raises(ValidationError):
        Review(order_id='X', text='t', rating=0)  # type: ignore[arg-type]
