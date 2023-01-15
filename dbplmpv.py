import sqlite3


class DbPlMpv:

    ''' Sqlite Pdlnmpv '''

    def __init__(self, table_name: str, db_file: str):
        self._table = table_name
        self._db = db_file
        self.conn = sqlite3.connect(self._db)
        self.cursor = self.conn.cursor()

        self.create_db()

    def create_db(self) -> None:
        self.cursor.execute(
            f'''
                CREATE TABLE IF NOT EXISTS {self._table}
                (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    title text NOT NULL,
                    watched bool NOT NULL,
                    deleted bool NOT NULL DEFAULT 0
                )
            '''
        )

    def create(self, title: str, watched: int, commit=True) -> None:
        self.cursor.execute(
            f'''
                INSERT INTO {self._table}
                (title, watched)
                VALUES ("{title}", {watched})
            '''
        )
        if commit:
            self.commit()

    def update(self, id: int, watched: int, commit: bool=True) -> None:
        '''
            watched: int = 0 or 1
        '''
        self.cursor.execute(
            f'''
                UPDATE {self._table}
                SET watched = {watched}
                WHERE id = {id}
            '''
        )
        if commit:
            self.commit()

    def read_filtered(self,
            watched: int | None = None, desc: bool = False, p: bool = True
                      ) -> list[dict[str, int | str]]:
        '''
            watched: int | None = 0, 1 or None
            p: bool = print or not
        '''
        rows: list[dict[str, int | str]] = []

        assert watched in [0, 1, None], 'watched must be 0 or 1'

        if watched is None:
            q = f'''
                    SELECT id, title
                    FROM "{self._table}"
                    WHERE deleted = 0
                '''
        else:
            q = f'''
                    SELECT id, title
                    FROM "{self._table}"
                    WHERE watched = {watched}
                    AND deleted = 0
                '''

        if desc:
            q += 'ORDER BY id DESC'

        for row in self.cursor.execute(q):
            _id: int = row[0]
            title: str = row[1]
            if p:
                print(f'{_id} - {title}')
            rows.append({'id': _id, 'title': title})
        return rows

    def read_all(self, nostate: bool = False, p: bool = True
                 ) -> list[dict[str, int | str]]:

        rows: list[dict[str, int | str]] = []
        for row in self.cursor.execute(
            f'''
                SELECT id, title, watched
                FROM "{self._table}"
                WHERE deleted = 0
                ORDER BY id DESC
            '''
        ):
            _id: int = row[0]
            title: str = row[1]
            watched: int = row[2]
            if p:
                if not nostate:
                    print(f'{_id} - {title} '
                          f'[{"watched" if watched else "unwatched"}]')
                else:
                    print(f'{_id} - {title}')
            rows.append({'id': _id, 'title': title})
        return rows

    def read_one(self, id: int, p: bool = True
                 ) -> list[dict[str, int | str]]:

        row = self.cursor.execute(
            f'''
                SELECT id, title
                FROM "{self._table}"
                WHERE id = {id}
            '''
        ).fetchone()

        if row:
            _id: int = row[0]
            title: str = row[1]
            if p:
                print(f'{_id} - {title}')
            return [{'id': _id, 'title': title}]
        else:
            print('Error: Not found')
            return [{'id': 0, 'title': ''}]

    def delete(self, ids: tuple[int, ...]) -> None:
        self.cursor.execute(
            f'''
                UPDATE {self._table}
                SET deleted = 1
                WHERE id IN {ids}
            '''
        )
        self.commit()

    def commit(self) -> None:
        ''' Commits to the database '''
        return self.conn.commit()

    def close(self) -> None:
        ''' Closes the database connection '''
        return self.conn.close()
