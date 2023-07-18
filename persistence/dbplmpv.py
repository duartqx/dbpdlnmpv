from argparse import Namespace
from pathlib import Path

import json
import os
import sqlite3


class DbPlMpv:

    """Sqlite Pdlnmpv"""

    def __init__(
        self,
        table_name: str,
        collection_table_name: str,
        db_file: str,
    ):
        self._table = table_name
        self._collection_table = collection_table_name
        self._db = db_file
        self.conn = sqlite3.connect(self._db)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create(
        self,
        entry: str,
        watched: int,
        collection: bool = False,
        commit: bool = True,
    ) -> None:
        """Creates one or more rows in the database"""

        entry_path: Path = Path(entry)

        if not collection:
            """It's not a collection and must insert a single row"""
            q: str = f"""
                INSERT INTO {self._table}
                (title, watched, path)
                VALUES (?, ?, ?)
            """

            title_watched_path_values: tuple[str, str, str] = (
                str(entry_path.name),
                str(watched),
                str(entry_path),
            )

            self.cursor.execute(q, title_watched_path_values)
        else:
            """
            If is collection then it means it's a folder that contains one or
            many seasons
            """

            values_to_insert: list[tuple[str, str, str]] = []

            VIDEO_EXTENSIONS: tuple[str, str, str] = (
                ".mkv",
                ".mp4",
                ".webm",
            )

            def insert_collection(
                path: Path, parent_collection_id: int | None
            ) -> int | None:
                q: str = f"""
                    INSERT INTO {self._collection_table}
                    (title, parent_collection_id)
                    VALUES (?, ?)
                """
                self.cursor.execute(q, (str(path.name), parent_collection_id))
                return self.cursor.lastrowid

            def crawl(path: Path, collection_id: int | None = None):
                if path.is_dir():
                    inner_collection_id = insert_collection(
                        path, collection_id
                    )
                    # Recurse
                    for p in sorted(path.iterdir(), key=lambda _p: _p.name):
                        crawl(p, inner_collection_id)

                elif (
                    path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
                ):
                    # row => (title, path, collection_id)
                    values_to_insert.append(
                        (
                            str(path.name),  # title
                            str(path),  # path
                            str(collection_id),  # collection_id
                        )
                    )

            collection_id: int | None = insert_collection(entry_path, None)
            for path in sorted(entry_path.iterdir(), key=lambda p: p.name):
                crawl(path, collection_id)

            if values_to_insert:
                q: str = f"""
                    INSERT INTO {self._table}
                    (title, watched, path, collection_id)
                    VALUES (?, {watched}, ?, ?)
                """

                self.cursor.executemany(q, values_to_insert)

        if commit:
            self.commit()

    def update_watched(self, id: int, commit: bool = True) -> None:
        q: str = f"""
            UPDATE {self._table}
            SET watched = (
                CASE
                    WHEN watched = 1
                    THEN 0
                    ELSE 1
                END
            )
            WHERE id = {id}
        """

        self.cursor.execute(q)

        if commit:
            self.commit()

    def read_filtered(
        self, watched: int, desc: bool = False
    ) -> list[dict[str, int | str]]:
        """
        Queries the database for all rows that are set to not deleted and that
        watched == watched

        watched: int | None = 0, 1 => watched or not
        desc: bool => Descending order
        """

        q: str = f"""
                SELECT id, title, watched, path
                FROM "{self._table}"
                WHERE watched = {watched}
                AND deleted = 0
                AND collection_id IS NULL
        """

        if desc:
            q += "ORDER BY id DESC"

        rows: list[dict[str, int | str]] = [
            dict(row) for row in self.cursor.execute(q).fetchall()
        ]
        return rows

    def read_all(self) -> list[dict[str, int | str]]:
        """Reads all rows from the database that aren't set to deleted"""

        q: str = f"""
            SELECT id, title, watched, path
            FROM "{self._table}"
            WHERE deleted = 0
            AND collection_id IS NULL
            ORDER BY id DESC
        """

        rows: list[dict[str, int | str]] = [
            dict(row) for row in self.cursor.execute(q).fetchall()
        ]
        return rows

    def read_one(self, id: int) -> dict[str, int | str]:
        """Queries the database for the row with id == id"""

        row = self.cursor.execute(
            f"""
                SELECT id, title, watched, path
                FROM "{self._table}"
                WHERE id = {id}
            """
        ).fetchone()

        return dict(row) if row else {}

    def _collection_query(self, collection_is: str) -> str:
        return f"""
            SELECT id, title
            FROM "{self._collection_table}"
            WHERE deleted = 0
            AND parent_collection_id {collection_is}
            ORDER BY id ASC
        """

    def read_parent_collections(self) -> list[dict[str, int | str]]:
        q: str = self._collection_query(collection_is="IS NULL")
        rows: list[dict[str, int | str]] = [
            dict(row) for row in self.cursor.execute(q).fetchall()
        ]
        return rows

    def read_inner_collection(
        self, collection_id: int
    ) -> list[dict[str, int | str]]:
        q: str = self._collection_query(collection_is="= ?")
        rows: list[dict[str, int | str]] = [
            dict(row)
            for row in self.cursor.execute(q, (collection_id,)).fetchall()
        ]
        return rows

    def read_collection(
        self, collection_id: int
    ) -> list[dict[str, int | str]]:
        q: str = f"""
            SELECT id, title, watched, path
            FROM "{self._table}"
            WHERE deleted = 0
            AND collection_id = ?
            ORDER BY id ASC
        """
        rows: list[dict[str, int | str]] = [
            dict(row)
            for row in self.cursor.execute(q, (collection_id,)).fetchall()
        ]
        return rows

    @staticmethod
    def _get_where(ids: tuple[int, ...]) -> str:
        if len(ids) > 1:
            return f"WHERE id IN {ids}"
        return f"WHERE id = {ids[0]}"

    def delete(self, ids: tuple[int, ...]) -> None:
        if ids:
            self.cursor.execute(
                f"""
                    UPDATE {self._table}
                    SET deleted = 1
                    {self._get_where(ids)}
                """
            )
            self.commit()

    def commit(self) -> None:
        """Commits to the database"""
        return self.conn.commit()

    def close(self) -> None:
        """Closes the database connection"""
        return self.conn.close()


class ConfigFileNotFoundError(Exception):
    pass


def get_connection() -> DbPlMpv:
    CONFIG_FILE: str = f"{os.environ['HOME']}/.config/dbmpv.json"
    if not Path(CONFIG_FILE).is_file():
        raise ConfigFileNotFoundError(
            "You need to have the config file with keys DB_FILE, "
            "TABLE_NAME and COLLECTION_TABLE_NAME"
        )
    with open(CONFIG_FILE, "r") as config_fh:
        config: Namespace = Namespace(**json.load(config_fh))

    return DbPlMpv(
        table_name=config.TABLE_NAME,
        collection_table_name=config.COLLECTION_TABLE_NAME,
        db_file=config.DB_FILE,
    )
