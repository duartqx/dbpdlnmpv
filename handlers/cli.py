from argparse import Namespace
from pathlib import Path

from persistence.dbplmpv import DbPlMpv
from service import (
    read_all,
    read_filtered,
    update,
)


async def cli_handler(db: DbPlMpv, args: Namespace) -> None:
    args.watched = int(args.watched)

    # Checks if the video file still exists in the playlist folder, if not
    # then updates its row to deleted=1
    if args.read or args.readall:
        db.delete(
            tuple(
                (
                    int(row["id"])
                    for row in db.read_all()
                    if not Path(f"{row['path']}").is_file()
                )
            )
        )

    if args.read:
        print((await read_filtered(db, ctx=args)).rstrip("\n"))
    elif args.readall:
        print((await read_all(db, withstatus=args.withstatus)).rstrip("\n"))
    elif args.update:
        await update(db, id=args.id)
    elif args.create:
        db.create(
            entry=args.create,
            collection=args.collection,
            watched=args.watched,
        )
