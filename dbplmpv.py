from pathlib import Path

import sqlite3
import os


class DbPlMpv:

    """Sqlite Pdlnmpv"""

    def __init__(
        self,
        table_name: str,
        db_file: str,
        base_dir: str = f"{os.environ['HOME']}/Media/Videos",
    ):
        self._table = table_name
        self._db = db_file
        self.base_dir = base_dir.rstrip("/")
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
        """Creates a row in the database"""

        entry_path: Path = Path(entry)

        if not collection:
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

            values_to_insert: list[tuple[str, str, str]] = [
                # Makes sure to add the entry_path without checks, we can mark
                # it as watched later if the folder is empty
                (
                    str(entry_path.name),
                    str(entry_path),
                    str(1),
                )
            ]

            collection__contents: list[Path] = sorted(
                entry_path.iterdir(), key=lambda p: p.name
            )

            collection_other_parents: list[Path] = []

            def add_path(p: Path):
                """
                If p.is_dir() then appends to collection_other_parents or a
                row to rows_to_insert
                """

                is_collection: int = int(p.is_dir())

                video_extensions: tuple[str, str, str] = (
                    ".mkv",
                    ".mp4",
                    ".webm",
                )

                there_is_any_video_in_the_collection: bool = (
                    any(
                        f.suffix.lower() in video_extensions
                        for f in p.glob("*")
                    )
                    if is_collection
                    else False
                )

                if is_collection and there_is_any_video_in_the_collection:
                    collection_other_parents.append(p)
                elif p.suffix.lower() in video_extensions:
                    # If it's a collection (and it's not empty) or is a video file, adds to rows
                    # row => (title, path, is_collection)
                    values_to_insert.append(
                        (
                            str(p.name),  # title
                            str(p),  # path
                            str(is_collection),  # is_collection
                        )
                    )

            for p in collection__contents:
                # Appends directories to collection_other_parents or rows to
                # rows_to_insert
                add_path(p)

            while collection_other_parents:
                # Loops throught until there's no more directories
                other_parent: Path = collection_other_parents.pop()

                for p in other_parent.iterdir():
                    add_path(p)

            q: str = f"""
                INSERT INTO {self._table}
                (title, watched, path, is_collection)
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
                SELECT id, title, path
                FROM "{self._table}"
                WHERE watched = {watched}
                AND deleted = 0
                AND is_collection = 0
        """

        if desc:
            q += "ORDER BY id DESC"

        rows: list[dict[str, int | str]] = [
            dict(row) for row in self.cursor.execute(q)
        ]
        return rows

    def read_all(self) -> list[dict[str, int | str]]:
        """Reads all rows from the database that aren't set to deleted"""

        q: str = f"""
            SELECT id, title, watched, path
            FROM "{self._table}"
            WHERE deleted = 0
            AND is_collection = 0
            ORDER BY id DESC
        """

        rows: list[dict[str, int | str]] = [
            dict(row) for row in self.cursor.execute(q)
        ]
        return rows

    def read_one(self, id: int) -> dict[str, int | str]:
        """Queries the database for the row with id == id"""

        row = self.cursor.execute(
            f"""
                SELECT id, title
                FROM "{self._table}"
                WHERE id = {id}
            """
        ).fetchone()

        if row:
            return dict(row)
        else:
            return {}

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
