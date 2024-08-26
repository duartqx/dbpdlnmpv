from abc import ABC
from dataclasses import dataclass

from domain.entities import Anime


class Event(ABC):
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
