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
    is not part of :attr:`metadata` or :attr:`delivery_fields`. Keys are
    casefolded labels, values are display strings. Input for
    :meth:`get_structured_fields`.
    """

    delivery_fields: Annotated[
        Mapping[str, str], BeforeValidator(OrderPage._convert_to_immutable)
    ] = MappingProxyType({})
    """
    Per-order delivery-contract data supplied by the buyer (Telegram username,
    Steam login, character name, email, …). Classified via the static
    blacklist in funpayparsers' ``ORDER_DELIVERY_LABELS`` at parse time;
    callers can re-classify with higher precision via
    :meth:`reclassify_with_structure` once a ``SubcategoryStructure`` with
    populated :attr:`SubcategoryStructure.delivery_fields` is available.
    """

    @staticmethod
    def _convert_to_immutable(value: Mapping[str, str]) -> MappingProxyType[str, str]:
        if isinstance(value, MappingProxyType):
            return value
        return MappingProxyType(dict(value))

    def get_structured_fields(self, structure: SubcategoryStructure) -> dict[str, str]:
        """
        Return ``lot_fields`` remapped to FunPay field IDs using *structure*'s
        label map. When labels are shared by multiple structure fields, uses
        the conditions of those fields against already-resolved entries to
        disambiguate.
        """
        result: dict[str, str] = {}
        for label, val in self.lot_fields.items():
            fid = structure.lookup_field_id(label, context=result)
            if fid is None:
                ids = structure.lower_label_map.get(label.casefold())
                if ids:
                    fid = ids[0]
            if fid is not None:
                result[fid] = val
        return result

    def reclassify_with_structure(
        self, structure: SubcategoryStructure
    ) -> OrderPage:
        """
        Re-split ``data`` using ``structure.delivery_fields`` for
        high-precision delivery classification. Useful when the page was
        originally parsed without structure context (only the static
        blacklist applied), and a populated ``SubcategoryStructure`` has
        since become available.

        Mutates ``self.lot_fields`` and ``self.delivery_fields``; returns
        ``self`` for chaining.
        """
        from funpayparsers.types.pages.order_page import _split_order_data
        extra = frozenset(
            label.casefold() for label in structure.delivery_fields.values()
        )
        _, lot_fields, delivery_fields = _split_order_data(
            dict(self.data), extra_delivery_labels=extra,
        )
        object.__setattr__(self, 'lot_fields', MappingProxyType(lot_fields))
        object.__setattr__(self, 'delivery_fields', MappingProxyType(delivery_fields))
        return self

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
