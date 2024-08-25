from abc import ABC, abstractmethod
from pathlib import Path
from types import TracebackType
from typing import Generic, Optional, Self, Type, TypeVar
import sqlite3

T = TypeVar("T")
Q = TypeVar("Q")

class Repository(ABC, Generic[T, Q]):

    conn: sqlite3.Connection
    cursor: sqlite3.Cursor
    auto_commit: bool

    database = Path.home() / ".local" / "share" / "playlists.db"
    basepath = Path.home() / "Media" / "Videos"

    @abstractmethod
    def insert(self, obj: T) -> None:
        raise NotImplementedError()

    @abstractmethod
    def update(self, obj: T) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_by_id(self, id: int) -> T:
        raise NotImplementedError()

    @abstractmethod
    def read(self, query: Q) -> list[T]:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, ids: tuple[int, ...]) -> int:
        raise NotImplementedError()

    def __init__(self, auto_commit: bool = True) -> None:
        self.auto_commit = auto_commit
        super().__init__()

    def __enter__(self) -> Self:
        self.conn = sqlite3.connect(self.database)

        self.cursor = self.conn.cursor()

        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        if exc_type is None and self.auto_commit:
            self.conn.commit()
        else:
            self.conn.rollback()

        self.conn.close()

        return False


# def get_connection(config: str) -> Repository:
#     from .dbplmpv import DbPlMpv
#
#     class ConfigFileNotFoundError(Exception):
#         pass
#
#     if not Path(config).is_file():
#         raise ConfigFileNotFoundError(CONFIG_NOT_FOUND_MSG)
#     with open(config, "r") as config_fh:
#         return DbPlMpv(config=Namespace(**json.load(config_fh)))
