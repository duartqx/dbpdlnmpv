from typing import Optional

from application.registry import registry, Registry
from application.listeners import *
from domain.events import Event
from repository import Repository


class MessageBus:
    repository: Repository

    def __init__(self, repository: Repository, registry: Registry = registry) -> None:
        self.repository = repository
        self.registry = registry

    def handle(self, event: Event):
        for listener in self.registry.get(event.__class__):
            listener(event)


bus: Optional[MessageBus] = None


def bootstrap(repository: Optional[Repository] = None) -> MessageBus:
    global bus

    if bus is None:
        assert (
            repository is not None
        ), "Repository is required to instantiate the message bus"
        bus = MessageBus(repository=repository)
    return bus
