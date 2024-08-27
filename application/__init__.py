from typing import Optional

from application.registry import registry
from application.listeners import *
from domain.events import Event
from repository import Repository


class MessageBus:
    repository: Repository

    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def handle(self, event: Event):
        for listener in registry.get(event.__class__):
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
