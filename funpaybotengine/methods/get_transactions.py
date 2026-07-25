from __future__ import annotations


__all__ = ['GetTransactions']

from typing import TYPE_CHECKING, Any

from funpayparsers.parsers import TransactionPreviewsParser

from funpaybotengine.types import TransactionPreviewsBatch
from funpaybotengine.types.enums import TransactionFilter
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import Bot


def make_data(m: GetTransactions, bot: Bot) -> dict[str, Any]:
    return {
        'filter': m.filter.value,
        'continue': str(m.from_transaction_id) if m.from_transaction_id > 0 else '',
        'user_id': str(bot.userid),
    }


class GetTransactions(FunPayMethod[TransactionPreviewsBatch]):
    """
    Get the main page method (``https://funpay.com/``).

    Returns ``funpaybotengine.types.pages.MainPage`` obj.
    """
    url = 'users/transactions'
    method = HTTPMethod.POST
    data = make_data
    parser_cls = TransactionPreviewsParser
    model_to_build = TransactionPreviewsBatch

    filter: TransactionFilter = TransactionFilter.ALL
    from_transaction_id: int = 0
