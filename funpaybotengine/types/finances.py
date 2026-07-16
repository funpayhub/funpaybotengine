from __future__ import annotations


__all__ = ('TransactionPreview', 'TransactionInfo', 'TransactionPreviewsBatch')


from types import MappingProxyType
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, field_validator
from funpayparsers.parsers.utils import parse_date_string

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import PaymentMethod, TransactionFilter, TransactionStatus
from funpaybotengine.types.common import MoneyValue


class TransactionPreview(FunPayObject, BaseModel):
    """Represents a transaction preview."""

    id: int
    """Unique transaction ID."""

    date_text: str
    """Transaction date (as human-readable text)."""

    desc: str
    """Transaction description."""

    status: TransactionStatus
    """Transaction status."""

    amount: MoneyValue
    """Transaction amount."""

    payment_method: PaymentMethod | None
    """Payment method, if applicable."""

    withdrawal_number: str | None
    """Withdrawal card / phone / wallet number, if applicable."""

    @property
    def timestamp(self) -> int:
        """
        Transaction timestamp.

        ``0``, if an error occurred while parsing.
        """
        try:
            return parse_date_string(self.date_text)
        except ValueError:
            return 0


class TransactionInfo(FunPayObject, BaseModel):
    """Represents a transaction info."""

    status: TransactionStatus
    """Transaction status."""

    data: Mapping[str, str]
    """Transaction data."""

    @field_validator('data', mode='before')
    @classmethod
    def _convert_to_immutable(cls, value: dict[str, str] | Mapping[str, str]) -> Mapping[str, str]:
        if isinstance(value, MappingProxyType):
            return value
        return MappingProxyType(dict(value))


class TransactionPreviewsBatch(FunPayObject, BaseModel):
    """
    Represents a single batch of transaction previews returned by FunPay.

    This batch contains a portion of all available transaction previews (typically 25),
    along with metadata required to fetch the next batch.
    """

    transactions: tuple[TransactionPreview, ...]
    """List of transaction previews included in this batch."""

    user_id: int | None
    """ID of the user to whom all transactions in this batch belong."""

    filter: TransactionFilter
    """
    Transactions filter applied to the current batch.

    The building method stamps this with the filter that was actually requested
    (see ``GetTransactions.transform_result``). The value scraped from the response
    HTML is only a fallback for hand-built objects, since FunPay omits the hidden
    ``filter`` input in some responses.

    ``None`` means the filter is unknown, which is not the same as
    ``TransactionFilter.ALL``.
    """

    next_transaction_id: int | None
    """
    ID of the next transaction to use as a cursor for pagination.

    If present, this value should be included in the next request to fetch
    the following batch of transaction previews.

    If ``None``, there are no more transactions to load.
    """

    @field_validator('filter', mode='before')
    @classmethod
    def _coerce_transaction_filter(cls, value: Any) -> TransactionFilter | None:
        try:
            return TransactionFilter(value)
        except ValueError:
            return TransactionFilter.UNKNOWN

    async def next_batch(self) -> TransactionPreviewsBatch:
        if not self.next_transaction_id:
            raise ValueError('Last batch.')

        return await self.get_bound_bot().get_transactions(
            from_transaction_id=self.next_transaction_id,
            filter=self.filter,
        )
