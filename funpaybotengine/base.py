from __future__ import annotations


__all__ = ('BindableObject', 'check_bound')


from typing import TYPE_CHECKING, Any, TypeVar
from collections.abc import Callable

from pydantic import BaseModel, PrivateAttr
from typing_extensions import Self

from funpaybotengine.exceptions import BotNotBoundError


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot


F = TypeVar('F', bound=Callable[..., Any])


class BindableObject(BaseModel):
    _bot: Bot | None = PrivateAttr(None)

    def model_post_init(self, context: dict[Any, Any]) -> None:
        self._bot = context.get('bot') if context else None

    def as_(self, bot: Bot | None, /) -> Self:
        self.bind_to(bot)
        return self

    def unbind(self) -> None:
        self._bot = None

    def bind_to(self, bot: Bot | None, /) -> None:
        self._bot = bot

    @property
    def bot(self) -> Bot | None:
        return self._bot

    def get_bound_bot(self) -> Bot:
        if not self.bot:
            raise BotNotBoundError(self)
        return self.bot


def check_bound(func: F) -> F:
    """
    Decorator for instance methods to ensure the object is bound to any Bot instance.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RuntimeError('Can be used only with instance methods.')

        if not isinstance(args[0], BindableObject):
            raise ValueError(f'{args[0].__class__.__name__} is not a bindable object.')
        if args[0].bot is None:
            raise RuntimeError(f'{args[0]} is not bound to any `Bot` instance.')
        return func(*args, **kwargs)

    return wrapper  # type: ignore
