from __future__ import annotations


__all__ = (
    'BotNotBoundError',
    'BotNotInitializedError',
    'BotUnauthenticatedError',
    'UserBannedError',
)

from typing import TYPE_CHECKING, Any

from .base import FunPayBotEngineError


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot


class BotNotBoundError(FunPayBotEngineError, RuntimeError):
    def __init__(self, obj: Any) -> None:
        self.obj = obj
        super().__init__(
            f'Instance of {obj.__class__.__name__} is not bound to any Bot instance.',
        )


class BotNotInitializedError(FunPayBotEngineError, RuntimeError):
    def __init__(self, bot: Bot) -> None:
        super().__init__(
            f'Bot instance {bot} is not initialized.\nUse `await bot.update()` to initialize it.',
        )


class BotUnauthenticatedError(FunPayBotEngineError, RuntimeError):
    def __init__(self) -> None:
        super().__init__(
            'Invalid golden key (maybe it is expired?).',
        )


class UserBannedError(FunPayBotEngineError, RuntimeError):
    def __init__(self) -> None:
        super().__init__(
            'Current account is banned.',
        )
