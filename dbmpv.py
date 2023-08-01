#!/usr/bin/env python
from argparse import ArgumentParser, Namespace
from handlers import cli_handler, fifo_handler

import asyncio

from options import get_options
from persistence.dbplmpv import DbPlMpv, get_connection


def get_args() -> Namespace:
    """
    Builds and returns main's parsed command line arguments

    OPTIONS:
        -f, --fifo: bool -> Starts the script in fifo mode and listen to commands
        -c, --create: str -> Title of the row to be created
        -d, --desc: bool -> Descending order
        -i, --id: int -> Row id
        -s, --withstatus: bool -> Prints row with watched status
        -p, --path: str -> The folder where the video files are stored
        -r, --read: bool -> Reads one line if id is passed or multiple rows by
                            watched status
        -R, --readall: bool -> Reads all rows without filter
        -u, --update: bool -> Updates watched status, requires id to be passed
        -w, --watched: bool -> 0 or 1 to be used when filtering by watched
                               status
        -C, --collection -> The entry is a collection/season
    """
    parser = ArgumentParser(prog="DbMpv-cli")

    for arg in get_options():
        parser.add_argument(*arg.pop("arg"), **arg)

    args = parser.parse_args()

    checker = sum(
        (
            bool(args.fifo),
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


async def main() -> None:
    db: DbPlMpv = get_connection()

    args: Namespace = get_args()

    with db.conn:
        if args.fifo:
            await fifo_handler(db=db)
        else:
            await cli_handler(db=db, args=args)


if __name__ == "__main__":
    asyncio.run(main())
