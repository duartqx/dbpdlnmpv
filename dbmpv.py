#!/usr/bin/env python
from click import command, option, UsageError
from dbplmpv import DbPlMpv
from os import environ
from sys import exit as _exit


HOME = environ.get('HOME')


@command()
@option("--db_file",
        default=f"{HOME}/.local/share/playlists.db",
        help="The sqlite db file")
@option("--table",
        prompt="What is the table name?", 
        help="The table that you want to read")
@option("--id", default=None, help="The id of the row.")
@option("--watched", default=0, help="Boolean 0 or 1")
@option("--title", default=None, help="Title of a row")
@option("--create", is_flag=True, help="Create option")
@option("--read", is_flag=True, help="Read option")
@option("--update", is_flag=True, help="Update option")
def main(db_file, table, id, watched, title, create, read, update):

    checker = sum([create, read, update])
    if not checker or checker > 1:
        raise UsageError(
            'Illegal usage: One of --create, --read and --update is required but they are mutually exclusive.'
            )

    # Database connection
    db = DbPlMpv(table, db_file)

    with db.conn:
        if read:
            if id:
                db.read_one(id)
            else:
                db.read_all(watched)
        elif create:
            if not title:
                raise UsageError('--title is required')
            else:
                db.create(title, watched)
        elif update:
            if not id:
                raise UsageError('--id is required')
            else:
                db.update(watched, id)


if __name__ == '__main__':
    main()