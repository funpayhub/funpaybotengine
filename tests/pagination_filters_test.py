from __future__ import annotations

import asyncio
from typing import Any, cast
from http import HTTPStatus

import pytest
from funpaybotengine.types.enums import TransactionFilter
from funpaybotengine.types.reviews import ReviewsBatch
from funpaybotengine.types.finances import TransactionPreviewsBatch
from funpaybotengine.client.session.base import RawResponse
from funpaybotengine.methods.get_reviews import GetReviews
from funpaybotengine.methods.get_transactions import GetTransactions


# Both ``users/reviews`` and ``users/transactions`` may answer without the hidden
# ``filter`` / ``user_id`` inputs, in which case the parser has nothing to read them from.
REVIEWS_HTML = """
<div class="review-container">
  <div class="review-item-date">2 месяца назад</div>
  <div class="review-item-text">Всё отлично</div>
  <div class="review-item-detail">Игра, 100 ₽</div>
  <div class="review-item-user"><a href="/users/777/"><img src="/img/a.jpg"/>
  <div class="media-user-name">Buyer</div></a></div>
</div>
"""

TRANSACTIONS_HTML = """
<div class="tc-item transaction-status-complete" data-transaction="10">
  <span class="tc-date-time">1 января, 12:00</span>
  <span class="tc-title">Заказ #ABCDEFGH</span>
  <div class="tc-price">+100 ₽</div>
</div>
"""


def raw_response(method: Any, html: str) -> RawResponse[Any]:
    return RawResponse(
        url='https://funpay.com/',
        status_code=HTTPStatus.OK,
        raw_response=html,
        headers={},
        cookies={},
        method_obj=method,
        context={},
        # Neither ``parse_result`` nor the parsers touch the bot.
        executed_as=cast(Any, None),
    )


def parse(method: Any, html: str) -> Any:
    return asyncio.run(method.parse_result(raw_response(method, html)))


def test_reviews_response_carries_no_filter_and_user_id() -> None:
    # Guards the premise of the fix: without the hidden inputs there is nothing to parse.
    from funpayparsers.parsers import ReviewsParser

    parsed = ReviewsParser(REVIEWS_HTML).parse()

    assert parsed.user_id is None
    assert parsed.filter is None


def test_get_reviews_stamps_requested_filter_and_user_id() -> None:
    parsed = parse(GetReviews(user_id=1234, filter='5'), REVIEWS_HTML)

    assert parsed.user_id == 1234
    assert parsed.filter == '5'


def test_get_transactions_stamps_requested_filter() -> None:
    parsed = parse(GetTransactions(filter=TransactionFilter.WITHDRAW), TRANSACTIONS_HTML)

    assert parsed.filter == TransactionFilter.WITHDRAW.value


def build_reviews_batch(**kwargs: Any) -> ReviewsBatch:
    return ReviewsBatch.model_validate(
        {
            'reviews': (),
            'user_id': None,
            'filter': None,
            'next_review_id': None,
            **kwargs,
        },
    )


def test_reviews_next_batch_rejects_last_batch() -> None:
    batch = build_reviews_batch(user_id=1234, filter='5')

    with pytest.raises(ValueError, match='Last batch.'):
        asyncio.run(batch.next_batch())


def test_reviews_next_batch_rejects_unknown_user() -> None:
    batch = build_reviews_batch(next_review_id='42')

    with pytest.raises(ValueError, match='Unknown user id.'):
        asyncio.run(batch.next_batch())


def test_reviews_next_batch_passes_cursor_and_filter() -> None:
    batch = build_reviews_batch(user_id=1234, filter='5', next_review_id='42')
    calls: list[dict[str, Any]] = []

    class BotStub:
        async def get_reviews(self, **kwargs: Any) -> ReviewsBatch:
            calls.append(kwargs)
            return batch

    batch.bind_to(cast(Any, BotStub()))
    asyncio.run(batch.next_batch())

    assert calls == [{'user_id': 1234, 'from_review_id': '42', 'filter': '5'}]


def test_transactions_next_batch_keeps_filter() -> None:
    batch = TransactionPreviewsBatch.model_validate(
        {
            'transactions': (),
            'user_id': None,
            'filter': TransactionFilter.WITHDRAW.value,
            'next_transaction_id': 42,
        },
    )
    calls: list[dict[str, Any]] = []

    class BotStub:
        async def get_transactions(self, **kwargs: Any) -> TransactionPreviewsBatch:
            calls.append(kwargs)
            return batch

    batch.bind_to(cast(Any, BotStub()))
    asyncio.run(batch.next_batch())

    assert calls == [{'from_transaction_id': 42, 'filter': TransactionFilter.WITHDRAW}]
