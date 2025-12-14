from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar
from asyncio import Lock

from funpayparsers.types import Language

from funpaybotengine.methods import FunPayMethod


if TYPE_CHECKING:
    from .bot import Bot
    from .session.base import Response


R = TypeVar('R', bound=Any)

lock = Lock()


async def force_locale_hook(
    method: FunPayMethod[R],
    bot: Bot,
    response: Response[R],
) -> Response[R]:
    async with lock:
        if bot.locale != Language.get_by_lang_code(response.locale):
            await bot.update(change_locale=bot._locale)
    return await method.execute(as_=bot)


async def ignore_locale_hook(
    method: FunPayMethod[R],
    bot: Bot,
    response: Response[R],
) -> Response[R]:
    return response
