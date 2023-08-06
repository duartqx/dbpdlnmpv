#!/usr/bin/env python
from argparse import Namespace

import asyncio
import os

from models import get_connection, DbPlMpv
from handlers.cli import get_cli_args, cli_handler


async def main() -> None:
    args: Namespace = get_cli_args()

    config: str = f"{os.environ['HOME']}/.config/dbmpv.json"
    db: DbPlMpv = get_connection(config)

    with db.conn:
        await cli_handler(db=db, args=args)


if __name__ == "__main__":
    asyncio.run(main())
