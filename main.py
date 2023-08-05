#!/usr/bin/env python
from argparse import Namespace
from pathlib import Path

import asyncio
import json
import os

from handlers import cli_handler
from args import get_args
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


def get_connection(config: str) -> DbPlMpv:
    class ConfigFileNotFoundError(Exception):
        pass

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
