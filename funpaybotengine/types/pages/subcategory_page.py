from __future__ import annotations


__all__ = ('SubcategoryPage',)


from pydantic import BaseModel

from funpaybotengine.types.enums import SubcategoryType
from funpaybotengine.types.offers import OfferPreview
from funpaybotengine.types.categories import Subcategory
from funpaybotengine.types.pages.base import FunPayPage
from funpaybotengine.types.subcategory_structure import SubcategoryStructure


class SubcategoryPage(FunPayPage, BaseModel):
    """
    Represents a subcategory offers list page
    (`https://funpay.com/<lots/chips>/<subcategory_id>/`)
    """

    category_id: int
    """Subcategory category ID."""

    subcategory_id: int
    """Subcategory ID."""

    subcategory_type: SubcategoryType
    """Subcategory type."""

    related_subcategories: tuple[Subcategory, ...] | None
    """List of related subcategories (including this one), if exists."""

    offers: tuple[OfferPreview, ...] | None
    """Subcategory offers list."""

    structure: SubcategoryStructure | None = None
    """
    Partial subcategory field structure, derived from the listing page's
    ``data-fields`` JSON and per-field form groups.

    This is a strict subset of the authenticated ``offerEdit`` schema:
    listing pages omit non-filterable fields (e.g. ``TEXTAREA``, ``IMAGES``)
    and may render option lists as button groups rather than ``<select>``.

    ``None`` when the page has no ``div.lot-fields`` block (e.g. chips).
    """
