from __future__ import annotations


__all__ = ['GetTransactionsPage']


from funpayparsers.parsers.page_parsers import TransactionsPageParser

from funpaybotengine.types.pages import TransactionsPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetTransactionsPage(FunPayMethod[TransactionsPage]):
    """Get the transactions page (``https://funpay.com/account/balance``)."""

    url = 'account/balance'
    method = HTTPMethod.GET
    parser_cls = TransactionsPageParser
    model_to_build = TransactionsPage

