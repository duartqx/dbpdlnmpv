from typing import cast
from application.registry import registry
from domain.events import Event, WasCreated, WereDeleted, WasUpdated
from repository import Repository


@registry.add(event=WasCreated)
def was_created_listener(repository: Repository, event: Event) -> None:
    event = cast(WasCreated, event)


@registry.add(event=WasUpdated)
def was_updated_listener(repository: Repository, event: Event) -> None:
    event = cast(WasUpdated, event)


@registry.add(event=WereDeleted)
def was_deleted_listener(repository: Repository, event: Event) -> None:
    event = cast(WereDeleted, event)
