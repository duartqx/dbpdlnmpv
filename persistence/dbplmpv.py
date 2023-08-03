from argparse import Namespace
from pathlib import Path

import json
import os
import sqlite3


class DbPlMpv:

    """Sqlite Pdlnmpv"""

    def __init__(self, config: Namespace):
        self.config: Namespace = config
        self.conn: sqlite3.Connection = sqlite3.connect(self.config.DB_FILE)
        self.conn.row_factory = sqlite3.Row
        self.__cursor: sqlite3.Cursor = self.conn.cursor()

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
                INSERT INTO {self.config.TABLE_NAME}
                (title, watched, path)
                VALUES (?, ?, ?)
            """

            title_watched_path_values: tuple[str, str, str] = (
                str(entry_path.name),
                str(watched),
                str(entry_path),
            )

            self.__cursor.execute(q, title_watched_path_values)
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
                    INSERT INTO {self.config.COLLECTION_TABLE_NAME}
                    (title, parent_collection_id)
                    VALUES (?, ?)
                """
                self.__cursor.execute(
                    q, (str(path.name), parent_collection_id)
                )
                return self.__cursor.lastrowid

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
                    INSERT INTO {self.config.TABLE_NAME}
                    (title, watched, path, collection_id)
                    VALUES (?, {watched}, ?, ?)
                """

                self.__cursor.executemany(q, values_to_insert)

        if commit:
            self.commit()

    def update_watched(self, id: int, commit: bool = True) -> None:
        q: str = f"""
            UPDATE {self.config.TABLE_NAME}
            SET watched = (
                CASE
                    WHEN watched = 1
                    THEN 0
                    ELSE 1
                END
            )
            WHERE id = ?
        """

        self.__cursor.execute(q, (id,))

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
            FROM "{self.config.TABLE_NAME}"
            WHERE watched = {watched}
            AND deleted = 0
            AND collection_id IS NULL
        """

        if desc:
            q += "ORDER BY id DESC"

        rows: list[dict[str, int | str]] = [
            dict(row) for row in self.__cursor.execute(q).fetchall()
        ]
        return rows

    def read_all(self) -> list[dict[str, int | str]]:
        """Reads all rows from the database that aren't set to deleted"""

        q: str = f"""
            SELECT id, title, watched, path
            FROM "{self.config.TABLE_NAME}"
            WHERE deleted = 0
            AND collection_id IS NULL
            ORDER BY id DESC
        """

        rows: list[dict[str, int | str]] = [
            dict(row) for row in self.__cursor.execute(q).fetchall()
        ]
        return rows

    def read_one(self, id: int) -> dict[str, int | str]:
        """Queries the database for the row with id == id"""

        row = self.__cursor.execute(
            f"""
                SELECT id, title, watched, path
                FROM "{self.config.TABLE_NAME}"
                WHERE id = {id}
            """
        ).fetchone()

        return dict(row) if row else {}

    def read_collections(self) -> list[dict[str, int | str]]:
        q: str = f"""
            SELECT id, title, watched, path
            FROM "{self.config.COLLECTION_TABLE_NAME}"
            WHERE deleted = 0
            AND parent_collection_id = NULL
            ORDER BY id ASC
        """
        rows: list[dict[str, int | str]] = [
            dict(row) for row in self.__cursor.execute(q).fetchall()
        ]
        return rows

    def read_collection(
        self, collection_id: int
    ) -> list[dict[str, int | str]]:
        q: str = f"""
            SELECT *
            FROM (
                SELECT
                    id,
                    title,
                    watched,
                    path,
                    "{self.config.TABLE_NAME}" AS source,
                    collection_id
                FROM "{self.config.TABLE_NAME}"
                WHERE collection_id = ?
                AND watched = 0
                AND deleted = 0

                UNION

                SELECT
                    id,
                    title,
                    watched,
                    COALESCE(path, '{self.config.BASE_PATH}' || title) AS path,
                    "{self.config.COLLECTION_TABLE_NAME}" AS source,
                    parent_collection_id AS collection_id
                FROM "{self.config.COLLECTION_TABLE_NAME}"
                WHERE parent_collection_id = ?
                AND watched = 0
                AND deleted = 0

            ) AS result;
        """
        rows: list[dict[str, int | str]] = [
            dict(row)
            for row in self.__cursor.execute(
                q, (collection_id, collection_id)
            ).fetchall()
        ]
        return rows

    @staticmethod
    def _get_where(ids: tuple[int, ...]) -> str:
        if len(ids) > 1:
            return f"WHERE id IN {ids}"
        return f"WHERE id = {ids[0]}"

    def delete(self, ids: tuple[int, ...]) -> None:
        if ids:
            self.__cursor.execute(
                f"""
                    UPDATE {self.config.TABLE_NAME}
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


CONFIG_NOT_FOUND_MSG: str = """$HOME/.config/dbmpv.json not found!

Sample config:

    {
        "BASE_PATH": "$HOME/Videos",
        "DB_FILE": "$HOME/.config/mydb.db",
        "TABLE_NAME": "mymaintable",
        "COLLECTION_TABLE_NAME": "mycollectiontablename"
    }

"""


def get_connection() -> DbPlMpv:
    CONFIG_FILE: str = f"{os.environ['HOME']}/.config/dbmpv.json"
    if not Path(CONFIG_FILE).is_file():
        raise ConfigFileNotFoundError(CONFIG_NOT_FOUND_MSG)
    with open(CONFIG_FILE, "r") as config_fh:
        config: Namespace = Namespace(**json.load(config_fh))

    return DbPlMpv(config=config)
