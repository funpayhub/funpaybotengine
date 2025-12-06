from __future__ import annotations


__all__ = ('GetSettingPage',)


from funpayparsers.parsers.page_parsers import SettingsPageParser

from funpaybotengine.types.pages import SettingsPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetSettingPage(FunPayMethod[SettingsPage]):
    """
    Get user settings page (``https://funpay.com/account/settings``).
    """

    __model_to_build__ = SettingsPage

    def __init__(self) -> None:
        super().__init__(
            url='account/settings',
            method=HTTPMethod.GET,
            parser_cls=SettingsPageParser,
            allow_anonymous=False,
            allow_uninitialized=True,
        )
