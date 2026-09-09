from __future__ import annotations


__all__ = ('SettingsPage',)

from funpaybotengine.types.settings import Settings
from funpaybotengine.types.pages.base import FunPayPage


class SettingsPage(FunPayPage):
    """Represents user settings page (``https://funpay.com/account/settings``)."""

    settings: Settings
    """User settings."""
