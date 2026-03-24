from __future__ import annotations


__all__ = ('SrasInfoPage',)


from funpaybotengine.types.sras import SrasSectionRestriction
from funpaybotengine.types.enums import SubcategoryType
from funpaybotengine.types.pages.base import FunPayPage


class SrasInfoPage(FunPayPage):
    """Represents the SRAS info page (``https://funpay.com/sras/info``)."""

    restrictions: dict[SubcategoryType, dict[int, SrasSectionRestriction]]
    """Restrictions grouped by subcategory type and subcategory ID."""
