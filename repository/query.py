from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class AnimeQueryOrder:
    by: Literal["title", "watched", "deleted"] = "title"
    direction: Literal["ASC", "DESC"] = "ASC"


@dataclass
class AnimeQuery:
    watched: Optional[bool] = None
    deleted: bool = False
    order: AnimeQueryOrder = AnimeQueryOrder()


@dataclass
class AnimeCollectionQuery:
    id: Optional[int] = None
    only_parent_collections: bool = True

    class Invalid(ValueError):
        def __init__(self, *args: object) -> None:
            super().__init__(
                "You need to pass an id or only_parent_collection must be True", *args
            )
