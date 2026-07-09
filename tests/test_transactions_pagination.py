from __future__ import annotations

from typing import Any
from http import HTTPStatus

import pytest
from funpaybotengine.types.enums import TransactionFilter
from funpaybotengine.types.finances import TransactionPreviewsBatch
from funpaybotengine.client.session.base import RawResponse
from funpaybotengine.methods.get_transactions import GetTransactions
from funpaybotengine.methods.get_transactions_page import GetTransactionsPage


# A real ``users/transactions`` response: it carries a ``continue`` cursor but no
# hidden ``filter`` input, which is exactly the shape that used to widen the filter.
RESPONSE_WITHOUT_FILTER_INPUT = """
<div class="tc-item transaction-status-complete" data-transaction="123">
  <span class="tc-date-time">1 июля, 12:00</span>
  <span class="tc-title">Вывод средств</span>
  <div class="tc-price">-100 &#8381;</div>
</div>
<input type="hidden" name="user_id" value="777">
<input type="hidden" name="continue" value="456">
"""


class BotStub:
    """Records the arguments ``next_batch()`` forwards to ``Bot.get_transactions``."""

    userid = 777

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def get_transactions(
        self,
        from_transaction_id: int = 0,
        filter: TransactionFilter | str = TransactionFilter.ALL,
    ) -> None:
        self.calls.append({'from_transaction_id': from_transaction_id, 'filter': filter})


def make_batch(
    *,
    scraped_filter: str | None,
    context: dict[str, Any] | None = None,
    next_transaction_id: int | None = 42,
) -> TransactionPreviewsBatch:
    return TransactionPreviewsBatch.model_validate(
        {
            'raw_source': '<html></html>',
            'transactions': (),
            'user_id': 1,
            'filter': scraped_filter,
            'next_transaction_id': next_transaction_id,
        },
        context=context,
    )


async def test_get_transactions_exposes_requested_filter_via_context() -> None:
    method = GetTransactions(filter=TransactionFilter.WITHDRAW)

    context = await method.get_context(None)  # type: ignore[arg-type]

    assert context['transaction_filter'] is TransactionFilter.WITHDRAW


async def test_get_transactions_accepts_no_arguments() -> None:
    method = GetTransactions()

    assert method.from_transaction_id == 0
    assert method.filter is TransactionFilter.ALL


async def test_requested_filter_wins_over_missing_hidden_input() -> None:
    batch = make_batch(
        scraped_filter=None,
        context={'transaction_filter': TransactionFilter.WITHDRAW},
    )

    assert batch.filter is TransactionFilter.WITHDRAW


async def test_next_batch_keeps_requested_filter() -> None:
    bot = BotStub()
    batch = make_batch(
        scraped_filter=None,
        context={'transaction_filter': TransactionFilter.WITHDRAW},
    )
    batch.bind_to(bot)  # type: ignore[arg-type]

    await batch.next_batch()

    assert bot.calls == [{'from_transaction_id': 42, 'filter': TransactionFilter.WITHDRAW}]


async def test_next_batch_preserves_all_filter() -> None:
    bot = BotStub()
    batch = make_batch(
        scraped_filter='',
        context={'transaction_filter': TransactionFilter.ALL},
    )
    batch.bind_to(bot)  # type: ignore[arg-type]

    await batch.next_batch()

    assert bot.calls == [{'from_transaction_id': 42, 'filter': TransactionFilter.ALL}]


async def test_next_batch_falls_back_to_scraped_filter_without_context() -> None:
    bot = BotStub()
    batch = make_batch(scraped_filter='withdraw')
    batch.bind_to(bot)  # type: ignore[arg-type]

    await batch.next_batch()

    assert bot.calls == [{'from_transaction_id': 42, 'filter': TransactionFilter.WITHDRAW}]


async def test_next_batch_raises_when_filter_is_unknown() -> None:
    batch = make_batch(scraped_filter=None)
    batch.bind_to(BotStub())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match='Unknown transaction filter.'):
        await batch.next_batch()


async def test_next_batch_raises_on_last_batch() -> None:
    batch = make_batch(scraped_filter='withdraw', next_transaction_id=None)
    batch.bind_to(BotStub())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match='Last batch.'):
        await batch.next_batch()


async def test_transactions_page_batch_is_marked_as_unfiltered() -> None:
    context = await GetTransactionsPage().get_context(None)  # type: ignore[arg-type]

    assert context['transaction_filter'] is TransactionFilter.ALL


async def test_filtered_pagination_survives_a_response_without_filter_input() -> None:
    bot = BotStub()
    method = GetTransactions(filter=TransactionFilter.WITHDRAW)
    response: RawResponse[TransactionPreviewsBatch] = RawResponse(
        url='https://funpay.com/users/transactions',
        status_code=HTTPStatus.OK,
        raw_response=RESPONSE_WITHOUT_FILTER_INPUT,
        headers={},
        cookies={},
        method_obj=method,
        context={},
        executed_as=bot,  # type: ignore[arg-type]
    )

    batch = await method.to_obj(response)
    await batch.next_batch()

    assert batch.filter is TransactionFilter.WITHDRAW
    assert bot.calls == [{'from_transaction_id': 456, 'filter': TransactionFilter.WITHDRAW}]
