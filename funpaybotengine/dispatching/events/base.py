from __future__ import annotations


__all__ = ('Event', 'RunnerEvent', 'BotEngineEvent', 'ExceptionEvent')

from typing import Any, Generic, TypeVar
from types import MappingProxyType

from pydantic import Field, PrivateAttr
from eventry.asyncio.event import Event as EventryEvent

from funpaybotengine.base import BindableObject


EventObject = TypeVar('EventObject')


# Not inheriting from ExtendedEvent, cz __iter__ conflict is pydantic BaseModel.
class Event(EventryEvent, BindableObject, Generic[EventObject], name='event'):
    model_config = {
        'arbitrary_types_allowed': True,
    }
    object: EventObject = Field(frozen=True)

    _data: dict[Any, Any] = PrivateAttr(default_factory=dict)
    _flags: set[Any] = PrivateAttr(default_factory=set)

    @property
    def event_context_injection(self) -> dict[str, Any]:
        return {'object': self.object}

    def __hash__(self) -> int:
        return id(self)

    def __setitem__(self, key: Any, value: Any) -> None:
        self._data[key] = value

    def __getitem__(self, key: Any) -> Any:
        return self._data[key]

    def __contains__(self, key: Any) -> bool:
        return key in self._data

    def set_flag(self, flag: Any) -> None:
        self._flags.add(flag)

    def set_flags(self, *flags: Any) -> None:
        self._flags.update(flags)

    def unset_flag(self, flag: Any) -> None:
        if flag in self._flags:
            self._flags.remove(flag)

    def unset_flags(self, *flags: Any) -> None:
        self._flags.difference_update(flags)

    def has_flag(self, flag: Any) -> bool:
        return flag in self._flags

    @property
    def flags(self) -> frozenset[Any]:
        return frozenset(self._flags)

    @property
    def data(self) -> MappingProxyType[Any, Any]:
        return MappingProxyType(self._data)


class RunnerEvent(Event[EventObject], name='runner'):
    tag: str | None = Field(frozen=True)

    @property
    def event_context_injection(self) -> dict[str, Any]:
        injection = super().event_context_injection
        injection['tag'] = self.tag
        return injection


class BotEngineEvent(Event[EventObject], name='funpaybotengine'): ...


class ExceptionEvent(BotEngineEvent[Exception], name='error'):
    event: Event[Any] = Field(frozen=True)

    @property
    def event_context_injection(self) -> dict[str, Any]:
        injection = super().event_context_injection
        injection.update({'on_event': self.event, 'exception': self.object})
        return injection
