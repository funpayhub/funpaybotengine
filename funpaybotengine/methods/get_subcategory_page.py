from __future__ import annotations


__all__ = ('GetSubcategoryPage',)


from pydantic import BaseModel
from funpayparsers.types import Language
from funpayparsers.parsers.page_parsers import SubcategoryPageParser
from funpayparsers.parsers.page_parsers.subcategory_page_parser import (
    SubcategoryPageParsingOptions,
)

from funpaybotengine.types.enums import SubcategoryType
from funpaybotengine.types.pages import SubcategoryPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetSubcategoryPage(FunPayMethod[SubcategoryPage], BaseModel):
    """
    Get a subcategory page method (``https://funpay.com/<lots/chips>/<subcategory_id>/``).

    Returns ``funpaybotengine.types.pages.SubcategoryPage`` obj.
    """

    type: SubcategoryType
    """Subcategory type."""

    subcategory_id: int
    """Subcategory ID."""

    __model_to_build__ = SubcategoryPage

    def __init__(
        self,
        type: SubcategoryType,
        subcategory_id: int,
        locale: Language | None = None,
        options: SubcategoryPageParsingOptions | None = None,
    ):
        super().__init__(
            url=f'{type.url_alias}/{subcategory_id}/',
            method=HTTPMethod.GET,
            allow_anonymous=True,
            allow_uninitialized=True,
            parser_cls=SubcategoryPageParser,
            parser_options=options,
            locale=locale,
            type=type,
            subcategory_id=subcategory_id,
        )
