from __future__ import annotations


__all__ = ('OfferPage',)


from pydantic import Field

from funpaybotengine.types.chat import Chat
from funpaybotengine.types.common import PaymentOption, DetailedUserBalance
from funpaybotengine.types.pages.base import FunPayPage
from funpaybotengine.types.subcategory_structure import SubcategoryStructure


class OfferPage(FunPayPage):
    subcategory_full_name: str
    """Full name of subcategory."""

    auto_delivery: bool
    """Whether auto-delivery is on or off."""

    fields: dict[str, str]
    """
    Offer fields from ``div.param-list``.

    Keys are human-readable FunPay labels (e.g. ``'Арена'``),
    values are display strings (e.g. ``'15'``).
    """

    chat: Chat
    """Chat with seller."""

    payment_options: dict[str, PaymentOption]
    """Payment options in format {variant_id: PaymentOption}."""

    user_balance: DetailedUserBalance  # user_balance available even on anonymous pages
    """User balance."""

    images: list[str] = Field(default_factory=list)
    """Full-size image URLs extracted from attachment items in ``div.param-list``."""

    delivery_fields_spec: dict[str, str] = Field(default_factory=dict)
    """
    Map of ``input.name → label`` for per-order delivery-contract fields
    rendered in the buyer's order form (``<form action="/orders/new">``).

    Keys are FunPay form input names (e.g. ``'player'``, ``'login'``);
    values are localized labels shown to the buyer (e.g.
    ``'Telegram Username'``, ``'Логин Steam'``). Includes both visible and
    conditionally-hidden form-groups.

    Use :meth:`SubcategoryStructure.enrich_delivery_fields_from_offer` to
    accumulate these into a per-subcategory delivery-label index.
    """

    def get_structured_fields(self, structure: SubcategoryStructure) -> dict[str, str]:
        """Return ``fields`` remapped to FunPay field IDs using *structure*'s label map."""
        return {
            structure.lower_label_map[label.lower()][0]: val
            for label, val in self.fields.items()
            if label.lower() in structure.lower_label_map
        }
