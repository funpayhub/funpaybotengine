from __future__ import annotations


__all__ = ('GetTransactionsPage',)


from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from funpayparsers.parsers.page_parsers import TransactionsPageParser

from funpaybotengine.types.enums import Language, TransactionFilter
from funpaybotengine.types.pages import TransactionsPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


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
        )

    async def transform_result(
        self,
        parsing_result: Any,
        response: RawResponse[Any],
    ) -> TransactionsPage:
        page = await super().transform_result(parsing_result, response)
        if page.transactions is not None:
            page.transactions.filter = TransactionFilter.ALL
        return page
