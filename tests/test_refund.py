"""`Refund.parse_result` must not turn every failure into a refused refund.

The bare `except` it used to carry caught `CancelledError` and
`KeyboardInterrupt` too, and re-raised them as `RefundError`. A task cancelled
mid-refund therefore reported "unable to refund" — while the request may well
have gone through.
"""

from __future__ import annotations

import json
import asyncio

import pytest
from funpaybotengine.exceptions import RefundError
from funpaybotengine.methods.refund import Refund


class _Response:
    def __init__(self, raw: str) -> None:
        self.raw_response = raw


@pytest.mark.asyncio
async def test_a_json_answer_without_an_error_is_a_refund() -> None:
    assert await Refund(order_id='X').parse_result(_Response(json.dumps({})))  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_the_sites_own_message_survives_into_the_error() -> None:
    with pytest.raises(RefundError) as caught:
        await Refund(order_id='X').parse_result(  # type: ignore[arg-type]
            _Response(json.dumps({'error': 1, 'msg': 'Заказ уже закрыт'}))
        )
    assert caught.value.message == 'Заказ уже закрыт'


@pytest.mark.asyncio
async def test_an_unparsable_answer_carries_why_and_chains_the_cause() -> None:
    """The reason used to be dropped: no cause, no text, just "unable"."""
    with pytest.raises(RefundError) as caught:
        await Refund(order_id='X').parse_result(_Response('<!doctype html>'))  # type: ignore[arg-type]
    assert isinstance(caught.value.__cause__, json.JSONDecodeError)
    assert 'Unable to refund order X: ' in caught.value.message
    assert caught.value.message != 'Unable to refund order X'


@pytest.mark.asyncio
async def test_cancellation_is_not_a_refused_refund() -> None:
    """The one that cannot pass on the parent commit.

    `CancelledError` derives from `BaseException`, so a bare `except` swallows
    it and reports a refusal for an order whose request may already be in
    flight.
    """

    class _Cancelling:
        @property
        def raw_response(self) -> str:
            raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await Refund(order_id='X').parse_result(_Cancelling())  # type: ignore[arg-type]
