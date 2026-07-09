from __future__ import annotations


__all__ = ('GetTransactionsPage',)


from pydantic import BaseModel
from funpayparsers.parsers.page_parsers import TransactionsPageParser

from funpaybotengine.types.enums import Language, TransactionFilter
from funpaybotengine.types.pages import TransactionsPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetTransactionsPage(FunPayMethod[TransactionsPage], BaseModel):
    """Get the transactions page (``https://funpay.com/account/balance``)."""

    __model_to_build__ = TransactionsPage

    def __init__(self, locale: Language | None = None):
        super().__init__(
            url='account/balance',
            method=HTTPMethod.GET,
            locale=locale,
            parser_cls=TransactionsPageParser,
            allow_anonymous=False,
            allow_uninitialized=True,
            # The balance page always renders an unfiltered transaction list.
            context={'transaction_filter': TransactionFilter.ALL},
        )
