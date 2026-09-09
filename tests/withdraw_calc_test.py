from __future__ import annotations

import asyncio
from typing import Any, cast

import pytest
from pydantic import ValidationError
from funpaybotengine.methods import WithdrawCalc
from funpaybotengine.types.withdraw import WithdrawCalcResult


def build_data(**kwargs: Any) -> dict[str, Any]:
    method = WithdrawCalc(
        currency_id='rub',
        ext_currency_id='card_rub',
        wallet='2202200000000000',
        **kwargs,
    )
    # ``make_data`` never touches the bot, so no session is needed to build the body.
    return asyncio.run(method.get_data(cast(Any, None)))


def test_leading_amount_ext_is_sent_and_amount_int_is_dropped() -> None:
    data = build_data(amount_ext=500_000)

    assert data == {
        'preview': '1',
        'currency_id': 'rub',
        'ext_currency_id': 'card_rub',
        'wallet': '2202200000000000',
        'amount_ext': 500_000,
    }


def test_leading_amount_int_is_sent_and_amount_ext_is_dropped() -> None:
    data = build_data(amount_int=500_000)

    assert 'amount_ext' not in data
    assert data['amount_int'] == 500_000


@pytest.mark.parametrize(
    'amounts',
    [
        {},
        {'amount_int': 1, 'amount_ext': 2},
    ],
)
def test_exactly_one_amount_is_required(amounts: dict[str, float]) -> None:
    with pytest.raises(ValidationError, match='Exactly one of'):
        WithdrawCalc(
            currency_id='rub',
            ext_currency_id='card_rub',
            wallet='2202200000000000',
            **amounts,
        )


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('500 000,5', 500_000.5),
        ('500\xa0000,5', 500_000.5),
        ('1000', 1000.0),
        (1000, 1000.0),
        ('', None),
        (None, None),
    ],
)
def test_amounts_are_normalized(raw: object, expected: float | None) -> None:
    result = WithdrawCalcResult.model_validate({'amount_int': raw})

    assert result.amount_int == expected


def test_only_the_calculated_amount_comes_back() -> None:
    # FunPay answers with the field that was not sent; the other one stays absent.
    result = WithdrawCalcResult.model_validate({'amount_int': '499 000'})

    assert result.amount_int == 499_000
    assert result.amount_ext is None
