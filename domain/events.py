from dataclasses import dataclass

from domain.entities import Anime


@dataclass
class Event:
    def __post_init__(self) -> None:
        pass


@dataclass
class WasUpdated(Event):
    anime: Anime


@dataclass
class WasCreated(Event):
    anime: Anime


@dataclass
class WereDeleted(Event):
    animes: list[Anime]
