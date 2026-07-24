from __future__ import annotations


__all__ = ['GetMainPage']


from funpayparsers.parsers.page_parsers import MainPageParser

from funpaybotengine.types.enums import Language
from funpaybotengine.types.pages import MainPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetMainPage(FunPayMethod[MainPage]):
    """
    Get the main page method (``https://funpay.com/``).

    Returns ``funpaybotengine.types.pages.MainPage`` obj.
    """
    url = ''
    method = HTTPMethod.GET
    data = lambda m, *_: {'setlocale': m.change_locale.appdata_alias} if m.change_locale else {}
    allow_anonymous = True
    allow_uninitialized = True
    parser_cls = MainPageParser
    model_to_build = MainPage

    change_locale: Language | None = None
    """
    Change locale to specified.
    
    Defaults to ``None``.
    """
