from __future__ import annotations


__all__ = ('OrderPage',)


import re
from typing import Annotated
from types import MappingProxyType
from collections.abc import Mapping

from pydantic import BaseModel, BeforeValidator
from funpayparsers.parsers.utils import parse_money_value_string

from funpaybotengine.types.chat import Chat
from funpaybotengine.types.enums import OrderStatus, SubcategoryType
from funpaybotengine.types.common import MoneyValue
from funpaybotengine.types.reviews import Review
from funpaybotengine.types.pages.base import FunPayPage
from funpaybotengine.types.subcategory_structure import SubcategoryStructure


class OrderPage(FunPayPage, BaseModel):
    """Represents an order page (`https://funpay.com/orders/<order_id>/`)."""

    order_id: str
    """Order ID."""

    order_status: OrderStatus
    """Order status."""

    delivered_goods: tuple[str, ...] | None
    """List of delivered goods."""

    images: tuple[str, ...] | None
    """List of attached images."""

    order_subcategory_id: int
    """Order subcategory id."""

    order_subcategory_type: SubcategoryType
    """Order subcategory type."""

    data: Annotated[Mapping[str, str], BeforeValidator(OrderPage._convert_to_immutable)]
    """
    Raw, flat ``param-list`` data — keys are casefolded labels.

    Kept for backwards compatibility. Prefer :attr:`metadata` for stable
    order-level fields and :attr:`lot_fields` for lot-specific fields.
    """

    review: Review | None
    """Order review."""

    chat: Chat
    """Chat with counterparty."""

    metadata: Annotated[
        Mapping[str, str], BeforeValidator(OrderPage._convert_to_immutable)
    ] = MappingProxyType({})
    """
    Stable order metadata keyed by canonical name. Possible keys: ``game``,
    ``category``, ``short_description``, ``detailed_description``, ``amount``,
    ``open``, ``closed``, ``total``. Only keys actually present on the page
    are stored.
    """

    lot_fields: Annotated[
        Mapping[str, str], BeforeValidator(OrderPage._convert_to_immutable)
    ] = MappingProxyType({})
    """
    Lot-specific fields from ``param-list`` — everything in :attr:`data` that
    is not part of :attr:`metadata`. Keys are casefolded labels, values are
    display strings. This is the input for :meth:`get_structured_fields`.
    """

    @staticmethod
    def _convert_to_immutable(value: Mapping[str, str]) -> MappingProxyType[str, str]:
        if isinstance(value, MappingProxyType):
            return value
        return MappingProxyType(dict(value))

    def get_structured_fields(self, structure: SubcategoryStructure) -> dict[str, str]:
        """Return ``lot_fields`` remapped to FunPay field IDs using *structure*'s label map."""
        return {
            structure.lower_label_map[label.casefold()][0]: val
            for label, val in self.lot_fields.items()
            if label.casefold() in structure.lower_label_map
        }

    @property
    def short_description(self) -> str | None:
        """Order short description (title)."""
        return self.metadata.get('short_description')

    @property
    def full_description(self) -> str | None:
        """Order full description (detailed description)."""
        return self.metadata.get('detailed_description')

    @property
    def amount(self) -> int | None:
        amount_str = self.metadata.get('amount')
        if not amount_str:
            return None
        return int(re.search(r'\d+', amount_str).group())  # type: ignore[union-attr]
        # always has \d+

    @property
    def open_date_text(self) -> str | None:
        """Order open date."""
        date_str = self.metadata.get('open')
        if not date_str:
            return None
        return date_str.split('\n')[0].strip()

    @property
    def close_date_text(self) -> str | None:
        """Order close date."""
        date_str = self.metadata.get('closed')
        if not date_str:
            return None
        return date_str.split('\n')[0].strip()

    @property
    def order_category_name(self) -> str | None:
        """Order category name."""
        return self.metadata.get('game')

    @property
    def order_subcategory_name(self) -> str | None:
        """Order subcategory name."""
        return self.metadata.get('category')

    @property
    def order_total(self) -> MoneyValue | None:
        """Order total."""
        value = self.metadata.get('total')
        if not value:
            return None
        money_value_string = parse_money_value_string(value)
        return MoneyValue.model_validate(money_value_string).as_(self.bot)
