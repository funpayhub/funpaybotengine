from __future__ import annotations

import asyncio
from typing import Any

import pytest
from funpayparsers.parsers import ReviewsParser, TransactionPreviewsParser
from funpaybotengine.types.enums import TransactionFilter
from funpaybotengine.types.reviews import ReviewsBatch
from funpaybotengine.types.finances import TransactionPreviewsBatch


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


def parse_reviews(context: dict[str, Any] | None = None) -> ReviewsBatch:
    return ReviewsBatch.model_validate(ReviewsParser(REVIEWS_HTML).parse(), context=context)


def parse_transactions(context: dict[str, Any] | None = None) -> TransactionPreviewsBatch:
    return TransactionPreviewsBatch.model_validate(
        TransactionPreviewsParser(TRANSACTIONS_HTML).parse(),
        context=context,
    )


def test_reviews_response_carries_no_filter_and_user_id() -> None:
    # Guards the premise of the fix: without the hidden inputs there is nothing to parse.
    batch = parse_reviews()

    assert batch.user_id is None
    assert batch.filter is None


def test_reviews_batch_prefers_requested_filter_and_user_id() -> None:
    batch = parse_reviews({'reviews_user_id': 1234, 'reviews_filter': '5'})

    assert batch.user_id == 1234
    assert batch.filter == '5'


def test_reviews_batch_keeps_parsed_values_without_context() -> None:
    # A batch nested in a profile page gets the page context, not a ``GetReviews`` one.
    batch = ReviewsBatch.model_validate(
        ReviewsParser(REVIEWS_HTML).parse(),
        context={'unrelated': 'context'},
    )

    assert batch.user_id is None
    assert batch.filter is None


def test_reviews_next_batch_rejects_last_batch() -> None:
    batch = parse_reviews({'reviews_user_id': 1234, 'reviews_filter': '5'})

    with pytest.raises(ValueError, match='Last batch.'):
        asyncio.run(batch.next_batch())


def test_reviews_next_batch_rejects_unknown_user() -> None:
    batch = parse_reviews()
    batch.next_review_id = '42'

    with pytest.raises(ValueError, match='Unknown user id.'):
        asyncio.run(batch.next_batch())


def test_reviews_next_batch_passes_cursor_and_filter() -> None:
    batch = parse_reviews({'reviews_user_id': 1234, 'reviews_filter': '5'})
    batch.next_review_id = '42'

    calls: list[dict[str, Any]] = []

    class BotStub:
        async def get_reviews(self, **kwargs: Any) -> ReviewsBatch:
            calls.append(kwargs)
            return batch

    batch.bind_to(BotStub())  # type: ignore[arg-type]  # only ``get_reviews`` is used
    asyncio.run(batch.next_batch())

    assert calls == [{'user_id': 1234, 'from_review_id': '42', 'filter': '5'}]


def test_transactions_response_carries_no_filter() -> None:
    assert parse_transactions().filter is None


def test_transactions_batch_prefers_requested_filter() -> None:
    batch = parse_transactions({'transactions_filter': TransactionFilter.WITHDRAW})

    assert batch.filter is TransactionFilter.WITHDRAW


def test_transactions_next_batch_keeps_filter() -> None:
    batch = parse_transactions({'transactions_filter': TransactionFilter.WITHDRAW})
    batch.next_transaction_id = 42

    calls: list[dict[str, Any]] = []

    class BotStub:
        async def get_transactions(self, **kwargs: Any) -> TransactionPreviewsBatch:
            calls.append(kwargs)
            return batch

    batch.bind_to(BotStub())  # type: ignore[arg-type]  # only ``get_transactions`` is used
    asyncio.run(batch.next_batch())

    assert calls == [{'from_transaction_id': 42, 'filter': TransactionFilter.WITHDRAW}]
