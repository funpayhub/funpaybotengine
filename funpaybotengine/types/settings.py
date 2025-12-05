from __future__ import annotations


__all__ = ('Settings',)


from funpaybotengine.types.base import FunPayObject


class Settings(FunPayObject):
    """Represents user settings (``https://funpay.com/account/settings``)."""

    telegram_username: str | None
    """Connected telegram account username."""

    telegram_notifications: bool
    """Whether telegram notifications are enabled."""

    push_notifications: bool
    """Whether push notifications are enabled."""

    email_notifications: bool
    """Whether email notifications are enabled."""

    offers_hidden: bool | None
    """Whether offers are hidden or not. Available only for salesmen."""
