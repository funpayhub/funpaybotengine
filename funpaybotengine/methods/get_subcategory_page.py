from __future__ import annotations


__all__ = ['GetSubcategoryPage']


from funpayparsers.parsers.page_parsers import SubcategoryPageParser

from funpaybotengine.types.enums import SubcategoryType
from funpaybotengine.types.pages import SubcategoryPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetSubcategoryPage(FunPayMethod[SubcategoryPage]):
    """
    Get a subcategory page method (``https://funpay.com/<lots/chips>/<subcategory_id>/``).

    Returns ``funpaybotengine.types.pages.SubcategoryPage`` obj.
    """

    url = lambda m, *_: f'{m.type.url_alias}/{m.subcategory_id}'
    method = HTTPMethod.GET
    allow_anonymous = True
    allow_uninitialized = True
    parser_cls = SubcategoryPageParser
    model_to_build = SubcategoryPage

    type: SubcategoryType
    """Subcategory type."""

    subcategory_id: int
    """Subcategory ID."""
