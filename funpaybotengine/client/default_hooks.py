from __future__ import annotations

from funpaybotengine.methods import FunPayMethod
from typing import Any, TypeVar

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .bot import Bot
    from .session.base import Response


R = TypeVar('R', bound=Any)


async def force_locale_hook(method: FunPayMethod[R], bot: Bot, response: Response[R]) -> Response[R]:
    await bot.update(change_locale=bot._locale)
    return await method.execute(as_=bot)


async def ignore_locale_hook(method: FunPayMethod[R], bot: Bot, response: Response[R]) -> Response[R]:
    return response

