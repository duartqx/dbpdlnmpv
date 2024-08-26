from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Generic, Optional, Self, Sequence, Type, TypeVar
import sqlite3

T = TypeVar("T")
Q = TypeVar("Q")


class Repository(ABC, Generic[T, Q]):

    conn: sqlite3.Connection
    cursor: Optional[sqlite3.Cursor]

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.cursor = None
        super().__init__()

    def __enter__(self) -> Self:
        if self.cursor is None:
            self.cursor = self.conn.cursor()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()

        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None

        return False

    def execute(self, sql: str, params: dict[str, Any]) -> sqlite3.Cursor:
        if self.cursor is None:
            self.cursor = self.conn.cursor()
        return self.cursor.execute(sql, params)


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
    def read(self, query: Q = (lambda: Q)()) -> list[T]:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, objs: Sequence[T]) -> int:
        raise NotImplementedError()
