#!/usr/bin/env python
from argparse import ArgumentParser, Namespace
from pathlib import Path

import asyncio
import json
import os

from handlers import cli_handler
from options import get_options
from persistence.dbplmpv import DbPlMpv

CONFIG_NOT_FOUND_MSG: str = """$HOME/.config/dbmpv.json not found!

Sample config:

    {
        "BASE_PATH": "$HOME/Videos",
        "DB_FILE": "$HOME/.config/mydb.db",
        "TABLE_NAME": "mymaintable",
        "COLLECTION_TABLE_NAME": "mycollectiontablename"
    }

"""


class ConfigFileNotFoundError(Exception):
    pass


def get_args() -> Namespace:
    """
    Builds and returns main's parsed command line arguments

    OPTIONS:
        -c, --create: str -> Title of the row to be created
        -C, --collection -> The entry is a collection/season
        -d, --desc: bool -> Descending order
        -i, --id: int -> Row id
        -s, --withstatus: bool -> Prints row with watched status
        -r, --read: bool -> Reads one line if id is passed or multiple rows by
                            watched status
        -R, --readall: bool -> Reads all rows without filter
        -u, --update: bool -> Updates watched status, requires id to be passed
        -D, --delete: bool -> Deletes from disk and sets deleted in the db
        -w, --watched: const int -> 0 or 1
    """
    parser = ArgumentParser(prog="DbMpv-cli")

    for arg in get_options():
        parser.add_argument(*arg.pop("arg"), **arg)

    args = parser.parse_args()

    checker = sum(
        (
            bool(args.create),
            bool(args.read),
            bool(args.readall),
        )
    )
    if not checker or checker > 1:
        parser.error(
            "Illegal usage: One of --create, --read, --readall, "
            "--choose_update, --update or --delete is required "
            "but they are mutually exclusive."
        )

    if not args.readall and (args.update and not args.id):
        parser.error("--id is required when only updating")

    return args


def get_connection(config: str) -> DbPlMpv:
    if not Path(config).is_file():
        raise ConfigFileNotFoundError(CONFIG_NOT_FOUND_MSG)
    with open(config, "r") as config_fh:
        return DbPlMpv(config=Namespace(**json.load(config_fh)))


async def main() -> None:
    config: str = f"{os.environ['HOME']}/.config/dbmpv.json"

    db: DbPlMpv = get_connection(config)

    args: Namespace = get_args()

    with db.conn:
        await cli_handler(db=db, args=args)


if __name__ == "__main__":
    asyncio.run(main())
