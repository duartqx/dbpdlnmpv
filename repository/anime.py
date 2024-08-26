from pathlib import Path
from typing import Sequence, override

from domain.entities import Anime
from repository import Repository
from repository.query import AnimeQuery

AnimeQueryResultSet = tuple[int, str, str, int, int]


class AnimeRepository(Repository[Anime, AnimeQuery]):

    @override
    def insert(self, obj: Anime) -> None:
        cursor = self.execute(
            f"""
            INSERT INTO animeplaylist
            (title, watched, path)
            VALUES (:title, :watched, :path)
            """,
            {"title": obj.title, "watched": int(obj.watched), "path": obj.path},
        )
        obj.id = cursor.lastrowid

    @override
    def update(self, obj: Anime) -> None:
        self.execute(
            f"""
            UPDATE animeplaylist
            SET watched = CASE WHEN watched = 1 THEN 0 ELSE 1 END
            WHERE id = :id
            """,
            {"id": obj.id},
        )
        obj.watched = not obj.watched

    @override
    def read(self, query: AnimeQuery = AnimeQuery()) -> list[Anime]:

        sql = [
            "SELECT id, title, path, watched, deleted",
            "FROM animeplaylist",
            "WHERE",
            "deleted = :deleted",
            "AND collection_id IS NULL",
        ]

        params = {
            "deleted": int(query.deleted),
        }

        if query.watched is not None:
            params["watched"] = int(query.watched)
            sql += ["AND watched = :watched"]

        sql += [f"ORDER BY {query.order.by} {query.order.direction}"]

        results: list[AnimeQueryResultSet] = self.execute(
            " ".join(sql), params
        ).fetchall()

        return [
            Anime(
                id=id,
                title=title,
                path=Path(path),
                watched=bool(watched),
                deleted=bool(deleted),
            )
            for id, title, path, watched, deleted in results
        ]

    @override
    def delete(self, objs: Sequence[Anime]) -> int:
        if not objs:
            return 0

        keys, values = [], {}
        for i, obj in enumerate(filter(lambda obj: obj.id, objs)):
            keys.append(f":id_{i}")
            values[f"id_{i}"] = obj.id

        cursor = self.execute(
            f"UPDATE animeplaylist SET deleted = 1 WHERE id in ({','.join(keys)})",
            values,
        )

        for obj in objs:
            obj.deleted = True

        return cursor.rowcount

    @override
    def get_by_id(self, id: int) -> Anime:
        title, path, watched, deleted = self.execute(
            """
            SELECT title, path, watched, deleted
            FROM animeplaylist
            WHERE id = :id
            """,
            {"id": id},
        ).fetchone()

        return Anime(
            id=id,
            title=title,
            path=Path(path),
            watched=bool(watched),
            deleted=bool(deleted),
        )
