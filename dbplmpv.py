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
                (id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                title text NOT NULL,
                watched bool NOT NULL)
            '''
        )
    
    def create(self, title: str, watched: int, commit=True) -> None:
        _exec = self.cursor.execute(
            f'''
                INSERT INTO {self._table}
                (title, watched)
                VALUES ("{title}", {watched})
            '''
        )
        if commit:
            self.commit()
    
    def read_all(self, watched: int) -> None:
        '''
            watched: int = 0 or 1
        '''
        for row in self.cursor.execute(
            f'''SELECT * FROM "{self._table}"
            WHERE watched = {watched}'''):
            _id: int = row[0]
            title: str = row[1]
            print(f'{title} - {_id}')

    def read_one(self, id: int) -> None:
        row = self.cursor.execute(
            f'''SELECT id, title FROM "{self._table}"
            WHERE id = {id}''').fetchone()
        _id: int = row[0]
        title: str = row[1]
        print(f'{title} - {_id}')

    def update_one(self, watched: int, id: int, commit=True) -> None:
        '''
            watched: int = 0 or 1
        '''
        _exec = self.cursor.execute(
            f'''UPDATE {self._table}
            SET watched = {watched}
            WHERE id = {id}''')
        if commit:
            self.commit()

    def commit(self) -> None:
        ''' Commits to the database '''
        return self.conn.commit()
    
    def close(self) -> None:
        ''' Closes the database connection '''
        return self.conn.close()