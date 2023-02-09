#!/usr/bin/env python
from click import command, option, UsageError
from dbplmpv import DbPlMpv
from os import environ
from pathlib import Path


HOME = environ.get("HOME")
PLAYLIST_FOLDER = f"{HOME}/Media/Videos"


@command()
@option(
    "--db_file", default=f"{HOME}/.local/share/playlists.db", help="The sqlite db file"
)
@option(
    "--table", prompt="What is the table name", help="The table that you want to read"
)
@option("--id", default=None, help="The id of the row.")
@option("--watched", default=0, help="Boolean 0 or 1")
@option("--create", help="Create option")
@option("--read", is_flag=True, help="Read option")
@option("--readall", is_flag=True, help="Read all option")
@option("--update_watched", is_flag=True, help="Update option")
@option("--nostate", is_flag=True, help="Read only the title option")
@option("--desc", is_flag=True, help="Descrescent flag")
@option("--delete", help="Change state to deleted")
def main(
    db_file: str,
    table: str,
    id: int,
    watched: int,
    create: str,
    read: bool,
    readall: bool,
    update_watched: bool,
    nostate: bool,
    desc: bool,
    delete: str,
) -> None:

    checker = sum(
        [
            bool(create),
            bool(read),
            bool(readall),
            bool(update_watched),
            bool(delete),
        ]
    )
    if not checker or checker > 1:
        raise UsageError(
            "Illegal usage: One of --create, --read, --readall, "
            "--update or --delete is required "
            "but they are mutually exclusive."
        )

    # Database connection
    db = DbPlMpv(table, db_file)

    with db.conn:

        # Clean up deleted files
        db.delete(
            tuple(
                (
                    int(row["id"])
                    for row in db.read_filtered(p=False)
                    if not Path(f'{PLAYLIST_FOLDER}/{row["title"]}').is_file()
                )
            )
        )

        if read:
            if id:
                db.read_one(id)
            elif desc:
                db.read_filtered(watched, desc=True)
            else:
                db.read_filtered(watched)
        elif readall:
            if nostate:
                db.read_all(nostate=True)
            else:
                db.read_all()
        elif update_watched:
            if not id:
                raise UsageError("--id is required")
            else:
                db.update_watched(id)
        elif create:
            db.create(create, watched)


if __name__ == "__main__":
    main()
