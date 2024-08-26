from pathlib import Path
from application.commands import (
    Index,
    ChooseWatch,
    ChooseWatchAndUpdate,
    ChooseAndUpdate,
    Delete,
    Purge,
    Create,
)
from domain.entities import Anime


def index():
    match Index().execute():
        case "Watch":
            return watch(watched=False, update=True)
        case "Update":
            return update()
        case "Watched":
            return watch(watched=True, update=False)
        case "Delete":
            return delete()
        case "Purge":
            return purge()


def watch(watched: bool = False, update: bool = False) -> bool:
    command = ChooseWatch(watched=watched)
    if update:
        command = ChooseWatchAndUpdate(watched=watched)

    return command.execute() is not None


def update() -> int:
    updated = ChooseAndUpdate().execute()
    return updated.id if updated and updated.id is not None else -1


def delete() -> None:
    return Delete().execute()


def purge() -> None:
    return Purge().execute()


def create(anime: Anime) -> int:
    return Create(anime=anime).execute()
