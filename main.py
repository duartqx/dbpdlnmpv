#!/usr/bin/env python
from argparse import ArgumentParser, Namespace
from pathlib import Path
from sqlite3 import Connection
from typing import Any, Final
import asyncio

from api.controllers import create, index
from application import bootstrap
from domain.entities import Anime
from repository.anime import AnimeRepository


Filename = str

DATABASE: Final[Path] = Path.home() / ".local" / "share" / "playlists.db"
BASEPATH: Final[Path] = Path.home() / "Media" / "Videos"


class DbMpvArgs(Namespace):
    create: list[Filename]


def get_options() -> tuple[dict[str, Any], ...]:
    return (
        {
            "arg": ("-c", "--create"),
            "help": "Create anime entry with the argument passed as title",
            "action": "store",
            "nargs": "*",
        },
    )


def get_args() -> DbMpvArgs:
    """
    Builds and returns main's parsed command line arguments

    OPTIONS:
        -c, --create: Filename
    """
    parser = ArgumentParser(prog="DbMpv-cli")

    for arg in get_options():
        parser.add_argument(*arg.pop("arg"), **arg)

    return parser.parse_args(namespace=DbMpvArgs())


async def main() -> None:
    args = get_args()

    with conn:
        if args.create:
            for title in args.create:
                create(Anime(title=title, path=BASEPATH / title))
        else:
            index()


if __name__ == "__main__":
    conn = Connection(database=DATABASE)

    bus = bootstrap(repository=AnimeRepository(conn=conn))

    with bus:
        asyncio.run(main())
