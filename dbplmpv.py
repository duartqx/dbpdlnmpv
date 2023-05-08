import sqlite3


class DbPlMpv:

    """Sqlite Pdlnmpv"""

    def __init__(self, table_name: str, db_file: str):
        self._table = table_name
        self._db = db_file
        self.conn = sqlite3.connect(self._db)
        self.cursor = self.conn.cursor()

        self.create_db()

    def create_db(self) -> None:
        self.cursor.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {self._table}
                (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    title text NOT NULL,
                    watched bool NOT NULL,
                    deleted bool NOT NULL DEFAULT 0
                )
            """
        )

    def create(self, title: str, watched: int, commit: bool = True) -> None:
        self.cursor.execute(
            f"""
                INSERT INTO {self._table}
                (title, watched)
                VALUES ("{title}", {watched})
            """
        )
        if commit:
            self.commit()

    def update_watched(self, id: int, commit: bool = True) -> None:
        self.cursor.execute(
            f"""
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
        )
        if commit:
            self.commit()

    def read_filtered(
        self, watched: int, desc: bool = False, echo: bool = True
    ) -> list[dict[str, int | str]]:
        """
        watched: int | None = 0, 1 or None
        echo: bool = print or not
        """
        rows: list[dict[str, int | str]] = []

        q = f"""
                SELECT id, title
                FROM "{self._table}"
                WHERE watched = {watched}
                AND deleted = 0
        """

        if desc:
            q += "ORDER BY id DESC"

        for _id, title in self.cursor.execute(q):
            if echo:
                print(f"{_id} - {title}")
            rows.append({"id": _id, "title": title})
        return rows

    def read_all(
        self, nostatus: bool = False, echo: bool = True
    ) -> list[dict[str, int | str]]:

        rows: list[dict[str, int | str]] = []
        for _id, title, watched in self.cursor.execute(
            f"""
                SELECT id, title, watched
                FROM "{self._table}"
                WHERE deleted = 0
                ORDER BY id DESC
            """
        ):
            if echo:
                if nostatus:
                    print(f"{_id} - {title}")
                else:
                    print(
                        f"{_id} - {title} "
                        f"[{'WATCHED' if watched else 'UNWATCHED'}]"
                    )
            rows.append({"id": _id, "title": title})
        return rows

    def read_one(
        self, id: int, echo: bool = True
    ) -> list[dict[str, int | str]]:

        row = self.cursor.execute(
            f"""
                SELECT id, title
                FROM "{self._table}"
                WHERE id = {id}
            """
        ).fetchone()

        if row:
            _id, title = row
            if echo:
                print(f"{_id} - {title}")
            return [{"id": _id, "title": title}]
        else:
            print("Error: Not found")
            return [{"id": 0, "title": ""}]

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
