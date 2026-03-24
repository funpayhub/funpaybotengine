from __future__ import annotations


__all__ = ('SrasSectionRestriction',)


from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import SubcategoryType


class SrasSectionRestriction(FunPayObject):
    """Represents a SRAS restriction for a specific subcategory."""

    subcategory_id: int
    """Subcategory ID."""

    subcategory_type: SubcategoryType
    """Subcategory type."""

    max_rating: int
    """Maximum allowed seller rating to be listed in this subcategory."""
