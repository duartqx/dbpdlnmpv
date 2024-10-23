from pathlib import Path
from application import MessageBus
from application.services import notify_send
from domain.events import WasCreated, WereDeleted, WasUpdated


@MessageBus.add_event_listener(event=WasCreated)
def notify_was_created(event: WasCreated) -> None:
    notify_send(f"Created: {event.anime.title}")


@MessageBus.add_event_listener(event=WasUpdated)
def notify_was_updated(event: WasUpdated) -> None:
    notify_send(
        f"""Updated: {event.anime.title}"""
        f""" {"[Watched]" if event.anime.watched else ""}"""
    )


@MessageBus.add_event_listener(event=WereDeleted)
def delete_from_disk(event: WereDeleted) -> None:
    def recusively_glob_and_delete(path: Path):
        if path.is_file():
            return path.unlink(missing_ok=True)

        for subpath in path.glob("*"):

            recusively_glob_and_delete(subpath)

            subpath.rmdir()

    for anime in event.animes:
        if anime.path.exists():
            recusively_glob_and_delete(anime.path)


@MessageBus.add_event_listener(event=WereDeleted)
def notify_were_deleted(event: WereDeleted) -> None:
    notify_send(f"Deleted: {', '.join(anime.title for anime in event.animes)}")
