from __future__ import annotations


__all__ = ('OrderPage',)


import re
from typing import Annotated, Any
from types import MappingProxyType
from datetime import datetime, timezone
from collections.abc import Mapping

from pydantic import BaseModel, BeforeValidator
from funpayparsers.parsers.utils import parse_date_string, parse_money_value_string

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

    def get_structured_delivery(
        self, structure: SubcategoryStructure | None = None,
    ) -> dict[str, str]:
        """
        Return ``delivery_fields`` keyed by canonical FunPay form input names.

        When *structure* is provided and its ``delivery_fields`` (label→name
        accumulator collected from ``OfferPage.delivery_fields_spec``) is
        populated, each delivery label is resolved to the original form
        ``input.name`` (``'player'``, ``'login'``, …). Without a structure
        — falls back to the raw casefolded labels FunPay rendered on the
        OrderPage.
        """
        if structure is None or not structure.delivery_fields:
            return dict(self.delivery_fields)
        # Reverse map: label_casefold → input_name
        reverse: dict[str, str] = {}
        for name, label in structure.delivery_fields.items():
            reverse[label.casefold()] = name
        result: dict[str, str] = {}
        for label, val in self.delivery_fields.items():
            key = reverse.get(label.casefold(), label)
            result[key] = val
        return result

    @staticmethod
    def _extract_lot_quantity(lot: Mapping[str, str]) -> int | None:
        """
        Best-effort numeric quantity extraction from already-resolved lot
        fields, as a fallback for orders where FunPay does not render the
        buyer-chosen quantity in ``metadata['amount']`` (e.g. Telegram Stars
        subcategory — quantity lives in ``lot['quantity'] = '50 звёзд'``).

        Looks at conventional FunPay quantity-bearing field ids in priority
        order, returns the leading integer or ``None``.
        """
        for fid in ('quantity', 'quantity2', 'amount'):
            raw = lot.get(fid)
            if raw is None:
                continue
            try:
                return int(raw)
            except (TypeError, ValueError):
                pass
            m = re.match(r'^\s*(\d+)', str(raw))
            if m:
                return int(m.group(1))
        return None

    def get_structured_context(
        self, structure: SubcategoryStructure | None = None,
    ) -> dict[str, Any]:
        """
        Unified structured view of the order combining lot, delivery and
        normalized order metadata in a single dict.

        Returned shape::

            {
                'lot':         {field_id: value, ...},  # via get_structured_fields
                'delivery':    {input_name|label: value, ...},  # via get_structured_delivery
                'amount':      int | None,
                'opened_at':   datetime | None,         # UTC
                'closed_at':   datetime | None,         # UTC
                'total':       MoneyValue | None,
                'category':    str | None,              # game name
                'subcategory': str | None,              # subcategory name
                'recipient':       str | None,          # first non-empty delivery value
                'recipient_label': str | None,
            }

        Invariants:

        * ``amount`` falls back from ``metadata['amount']`` to the leading
          integer of ``lot['quantity']`` / ``lot['quantity2']`` when the
          metadata value is missing — guarantees a numeric answer whenever
          quantity is anywhere in the order, regardless of which surface
          carried it.
        * ``recipient`` is populated whenever the order has any delivery
          input (Telegram username, Steam login, character name, email, …)
          — accessible without consulting ``delivery`` keys directly.
        * If *structure* is omitted, ``lot`` is empty and ``delivery`` keys
          are raw labels (no input-name mapping).
        """
        lot = self.get_structured_fields(structure) if structure else {}
        amount = self.amount
        if amount is None:
            amount = self._extract_lot_quantity(lot)
        return {
            'lot': lot,
            'delivery': self.get_structured_delivery(structure),
            'amount': amount,
            'opened_at': self.opened_at,
            'closed_at': self.closed_at,
            'total': self.order_total,
            'category': self.order_category_name,
            'subcategory': self.order_subcategory_name,
            'recipient': self.recipient,
            'recipient_label': self.recipient_label,
        }

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
        """Order open date as raw FunPay text (e.g. ``'23 апреля в 20:40 (...)'``).

        Prefer :attr:`opened_at` for a parsed ``datetime``.
        """
        date_str = self.metadata.get('open')
        if not date_str:
            return None
        return date_str.split('\n')[0].strip()

    @property
    def close_date_text(self) -> str | None:
        """Order close date as raw FunPay text. Prefer :attr:`closed_at`."""
        date_str = self.metadata.get('closed')
        if not date_str:
            return None
        return date_str.split('\n')[0].strip()

    @property
    def opened_at(self) -> datetime | None:
        """
        Order open timestamp parsed from ``metadata['open']``.

        Returns a UTC ``datetime`` (FunPay renders Europe/Moscow / UTC+3
        timestamps; :func:`funpayparsers.parsers.utils.parse_date_string`
        normalizes them to UTC). Returns ``None`` if missing or unparseable.
        """
        text = self.open_date_text
        if not text:
            return None
        try:
            return datetime.fromtimestamp(parse_date_string(text), tz=timezone.utc)
        except (ValueError, OverflowError, OSError):
            return None

    @property
    def closed_at(self) -> datetime | None:
        """Order close timestamp parsed from ``metadata['closed']``. UTC."""
        text = self.close_date_text
        if not text:
            return None
        try:
            return datetime.fromtimestamp(parse_date_string(text), tz=timezone.utc)
        except (ValueError, OverflowError, OSError):
            return None

    @property
    def recipient(self) -> str | None:
        """
        Best-effort buyer-supplied delivery target — returns the first
        non-empty value from :attr:`delivery_fields`.

        Common cases: Telegram username, Steam login, in-game character name,
        email. Returns ``None`` if no delivery fields were captured.
        """
        for v in self.delivery_fields.values():
            if v:
                return v
        return None

    @property
    def recipient_label(self) -> str | None:
        """Label of the field whose value is returned by :attr:`recipient`."""
        for label, v in self.delivery_fields.items():
            if v:
                return label
        return None

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
