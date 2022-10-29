import sqlite3
import logging
from sqlite3 import Cursor

from typing import Any


def connect(db: str):
    return sqlite3.connect(db)

def create_db(cursor: Cursor, db_name: str) -> Cursor:
    return cursor.execute(f'CREATE TABLE IF NOT EXISTS {db_name} (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, title text NOT NULL, watched bool NOT NULL)')

def create(cursor: Cursor, db_name: str, title: str, watched: int) -> Cursor:
    return cursor.execute(f'INSERT INTO {db_name} (title, watched) VALUES ("{title}", "{watched}")')

def read_all_unwatched(cursor: Cursor, db_name: str) -> None:
    for row in cursor.execute(f'SELECT * FROM "{db_name}" WHERE watched = 0'):
        _id = row[0]
        title = row[1]
        print(f'{title} - {_id}')

def read_one(cursor: Cursor, db_name: str, id: int, title: str) -> None:
    if id is not None:
        row = cursor.execute(f'SELECT id, title FROM "{db_name}" WHERE id = {id}').fetchone()
        _id = row[0]
        title = row[1]
        print(f'{title} - {_id}')
    elif title is not None:
        row = cursor.execute(f'SELECT id, title FROM "{db_name}" WHERE title = "{title}"').fetchone()
        _id = row[0]
        title = row[1]
        print(f'{title} - {_id}')
    else:
        print('You need to pass a filter!')

if __name__ == '__main__':

    dbfile = 'anime.db'
    db_name = 'animeplaylist'
    db = connect(dbfile)
    cursor = db.cursor()
    cursor = create_db(cursor, db_name)
    titles = [
        '[ASW] Noumin Kanren no Skill bakka Agetetara Nazeka Tsuyoku Natta - 05 [1080p HEVC][5870F24D].mkv',
        '[ASW]  bakka Agetetara Nazeka Tsuyoku Natta - 05 [1080p HEVC][5870F24D].mkv',
        '[ASW] Noumin Kanren no Skill bakka Agetetara 80p HEVC][5870F24D].mkv',
        '[ASW] Noumin Kanren no Skill yoku Natta - 05 [1080p HEVC][5870F24D].mkv',
        '[ASW] Noumiazeka Tsuyoku Natta - 05 [1080p HEVC][5870F24D].mkv',
        '[ASW] Noumin Kanren no Skill bak24D].mkv',
        ]
    
    #for title in titles:
    #    cursor = create(cursor=cursor,
    #                    db_name=dbname,
    #                    title=title,
    #                    watched=0)
    #read(cursor, dbname)
    read_one(cursor, db_name, id=4, title=None)
    read_one(cursor, db_name, id=None, title='[ASW] Noumin Kanren no Skill yoku Natta - 05 [1080p HEVC][5870F24D].mkv')
    db.commit()
    db.close()