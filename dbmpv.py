#!/usr/bin/env python
from argparse import ArgumentParser, Namespace
from cli_args import get_args
from dbplmpv import DbPlMpv
from pathlib import Path


def _get_args() -> Namespace:
    """
    Builds and returns main's parsed command line arguments

    ARGUMENTS:
        dbfile: str -> The sqlite database file, required
        table: str -> Table name on the database, required
    OPTIONS:
        -c, --create: str -> Title of the row to be created
        -d, --desc: bool -> Descending order
        -i, --id: int -> Row id
        -n, --nostatus: bool -> Prints only row title without watched status
        -p, --path: str -> The folder where the video files are stored
        -r, --read: bool -> Reads one line if id is passed or multiple rows by
                            watched status
        -R, --readall: bool -> Reads all rows without filter
        -u, --update: bool -> Updates watched status, requires id to be passed
        -w, --watched: bool -> 0 or 1 to be used when filtering by watched
                               status
    """
    parser = ArgumentParser(prog="DbMpv-cli")

    for arg in get_args():
        parser.add_argument(*arg.pop("arg"), **arg)

    args = parser.parse_args()

    checker = sum(
        (
            bool(args.create),
            bool(args.read),
            bool(args.readall),
            bool(args.update),
        )
    )
    if not checker or checker > 1:
        parser.error(
            "Illegal usage: One of --create, --read, --readall, "
            "--update or --delete is required "
            "but they are mutually exclusive."
        )

    if args.update and not args.id:
        parser.error("--id is required when updating")

    return args


def main() -> None:

    args: Namespace = _get_args()

    db = DbPlMpv(table_name=args.table, db_file=args.dbfile)

    with db.conn:

        watched = int(args.watched)

        # Checks if the video file still exists in the playlist folder, if not
        # then updates its row to deleted=1
        if (args.read or args.readall) and args.path:
            db.delete(
                tuple(
                    (
                        int(row["id"])
                        for row in db.read_all(echo=False)
                        if not Path(f"{args.path}/{row['title']}").is_file()
                    )
                )
            )

        if args.read:
            if args.id:
                db.read_one(id=args.id)
            else:
                db.read_filtered(watched=watched, desc=args.desc)
        elif args.readall:
            db.read_all(nostatus=args.nostatus)
        elif args.update:
            db.update_watched(id=args.id)
        else:
            db.create(title=args.create, watched=watched)


if __name__ == "__main__":
    main()
