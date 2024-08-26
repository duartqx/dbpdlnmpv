from typing import Callable, Type

from domain.events import Event
from repository import Repository


Listener = Callable[[Repository, Event], None]


class Registry:
    _mappings: dict[Type[Event], list[Listener]] = {}

    def add(self, event: Type[Event]) -> Callable[[Listener], Listener]:
        def wrapped(listener: Listener) -> Listener:
            self._mappings.setdefault(event, []).append(listener)
            return listener

        return wrapped

    def get(self, event: Type[Event]) -> list[Listener]:
        return self._mappings.get(event, [])


registry = Registry()
