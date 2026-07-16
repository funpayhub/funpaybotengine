from __future__ import annotations


__all__ = ('GetTransactions',)

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from funpayparsers.parsers import TransactionPreviewsParser

from funpaybotengine.types import TransactionPreviewsBatch
from funpaybotengine.types.enums import Language, TransactionFilter
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import Bot
    from funpaybotengine.client.session.base import RawResponse


class GetTransactions(FunPayMethod[TransactionPreviewsBatch], BaseModel):
    """
    Get the main page method (``https://funpay.com/``).

    Returns ``funpaybotengine.types.pages.MainPage`` obj.
    """

    filter: TransactionFilter = TransactionFilter.ALL
    from_transaction_id: int = 0

    __model_to_build__ = TransactionPreviewsBatch

    def __init__(
        self,
        filter: TransactionFilter | str = TransactionFilter.ALL,
        from_transaction_id: int = 0,
        locale: Language | None = None,
    ):
        super().__init__(
            url='users/transactions',
            method=HTTPMethod.POST,
            locale=locale,
            parser_cls=TransactionPreviewsParser,
            allow_anonymous=False,
            allow_uninitialized=False,
            data=make_data,
            filter=filter,
            from_transaction_id=from_transaction_id,
        )

    async def transform_result(
        self,
        parsing_result: Any,
        response: RawResponse[Any],
    ) -> TransactionPreviewsBatch:
        batch = await super().transform_result(parsing_result, response)
        batch.filter = self.filter
        return batch


async def make_data(method: GetTransactions, bot: Bot) -> dict[str, Any]:
    return {
        'filter': method.filter.value,
        'continue': str(method.from_transaction_id) if method.from_transaction_id > 0 else '',
        'user_id': str(bot.userid),
    }
