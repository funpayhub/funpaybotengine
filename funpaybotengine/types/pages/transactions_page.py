from __future__ import annotations


__all__ = ('TransactionsPage',)


from pydantic import BaseModel

from funpaybotengine.types.common import MoneyValue
from funpaybotengine.types.finances import TransactionPreviewsBatch
from funpaybotengine.types.pages.base import FunPayPage


class TransactionsPage(FunPayPage, BaseModel):
    """Represents the transactions page (https://funpay.com/account/balance)."""

    rub_balance: MoneyValue | None
    """RUB balance."""

    usd_balance: MoneyValue | None
    """USD balance."""

    eur_balance: MoneyValue | None
    """EUR balance."""

    deals_balance: MoneyValue | None
    """Deals balance."""

    transactions: TransactionPreviewsBatch | None
    """Transaction previews."""
