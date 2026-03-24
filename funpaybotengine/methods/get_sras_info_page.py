from __future__ import annotations


__all__ = ('GetSrasInfoPage',)


from funpayparsers.parsers.page_parsers import SrasInfoPageParser

from funpaybotengine.types.pages import SrasInfoPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


class GetSrasInfoPage(FunPayMethod[SrasInfoPage]):
    """
    Get SRAS info page (``https://funpay.com/sras/info``).

    Returns seller rating restrictions per subcategory.
    Returns ``funpaybotengine.types.pages.SrasInfoPage``.
    """

    __model_to_build__ = SrasInfoPage

    def __init__(self) -> None:
        super().__init__(
            url='sras/info',
            method=HTTPMethod.GET,
            parser_cls=SrasInfoPageParser,
        )
