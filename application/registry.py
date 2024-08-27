from typing import Callable, Generic, Type, TypeVar

from domain.events import Event

E = TypeVar("E", bound=Event)

Listener = Callable[[E], None]


class Registry(Generic[E]):
    _mappings: dict[Type[E], list[Listener]] = {}

    def add(self, event: Type[E]) -> Callable[[Listener], Listener]:
        def wrapped(listener: Listener) -> Listener:
            self._mappings.setdefault(event, []).append(listener)
            return listener

        return wrapped

    def get(self, event: Type[E]) -> list[Listener]:
        return self._mappings.get(event, [])


registry = Registry()
