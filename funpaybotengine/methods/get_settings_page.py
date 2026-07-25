from __future__ import annotations


__all__ = ['GetSettingPage']


from funpayparsers.parsers.page_parsers import SettingsPageParser

from funpaybotengine.types.pages import SettingsPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetSettingPage(FunPayMethod[SettingsPage]):
    """
    Get user settings page (``https://funpay.com/account/settings``).
    """

    url = 'account/settings'
    method = HTTPMethod.GET
    allow_uninitialized = True
    parser_cls = SettingsPageParser
    model_to_build = SettingsPage
