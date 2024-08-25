from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class Entity(ABC): ...


@dataclass
class Anime(Entity):
    title: str
    path: Path
    id: Optional[int] = None
    watched: bool = False
    deleted: bool = False
    collection_id: Optional[int] = None


@dataclass
class AnimeCollection(Entity):
    title: str
    path: Path
    id: Optional[int] = None
    watched: bool = False
    deleted: bool = False
    parent_collection_id: Optional[int] = None
