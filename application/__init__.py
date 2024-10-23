from dataclasses import is_dataclass
from queue import Queue
from types import TracebackType
from typing import Callable, Optional, Self, Type, TypeVar

from domain.events import Event
from repository import Repository


E = TypeVar("E", bound=Event)

Listener = Callable[[E], None]


registry: dict[Type[Event], list[Listener]] = {}


class MessageBus:
    queue: Queue[Event] = Queue()

    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_value: Optional[Exception],
        traceback: Optional[TracebackType],
    ) -> None:
        while self.queue.qsize():
            event = self.queue.get()
            self.handle(event)

    @classmethod
    def _register_event(cls, event: Type[E]) -> None:
        init = "__init__" if not is_dataclass(event) else "__post_init__"

        original_init = getattr(event, init, lambda self, *args, **kwargs: None)

        def overwritten_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            cls.queue.put(self)

        setattr(event, init, overwritten_init)
        setattr(event, "__registered_event__", True)

    @classmethod
    def add_event_listener(cls, event: Type[E]) -> Callable[[Listener], Listener]:

        if not getattr(event, "__registered_event__", False):
            cls._register_event(event)

        def wrapped(listener: Listener) -> Listener:

            registry.setdefault(event, []).append(listener)

            return listener

        return wrapped

    def handle(self, event: Event):
        for listener in registry.get(event.__class__, []):
            listener(event)


bus: Optional[MessageBus] = None


def bootstrap(repository: Optional[Repository] = None) -> MessageBus:
    import application.listeners as _

    global bus

    if bus is None:
        assert (
            repository is not None
        ), "Repository is required to instantiate the message bus"

        bus = MessageBus(repository=repository)
    return bus
