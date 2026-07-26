from __future__ import annotations


__all__ = ['GetProfilePage']


from funpayparsers.parsers.page_parsers import ProfilePageParser

from funpaybotengine.types.pages import ProfilePage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetProfilePage(FunPayMethod[ProfilePage]):
    """
    Get a profile page method (``https://funpay.com/users/<user_id>/``).

    Returns ``funpaybotengine.types.pages.ProfilePage`` obj.
    """

    url = lambda m, *_: f'users/{m.user_id}/'
    method = HTTPMethod.GET
    allow_anonymous = True
    allow_uninitialized = True
    parser_cls = ProfilePageParser
    model_to_build = ProfilePage

    user_id: int
    """User ID."""

