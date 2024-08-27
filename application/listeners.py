from application.registry import registry
from application.services import notify_send
from domain.events import WasCreated, WereDeleted, WasUpdated


@registry.add(event=WasCreated)
def was_created_listener(event: WasCreated) -> None:
    notify_send(f"Created: {event.anime.title}")


@registry.add(event=WasUpdated)
def was_updated_listener(event: WasUpdated) -> None:
    notify_send(f"Updated: {event.anime.title}")


@registry.add(event=WereDeleted)
def was_deleted_listener(event: WereDeleted) -> None:
    notify_send(f"Deleted: {', '.join(anime.title for anime in event.animes)}")
