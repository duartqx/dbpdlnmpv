from argparse import Namespace
from pathlib import Path

from models.dbplmpv import DbPlMpv
from controllers.cli import CliController


async def cli_handler(db: DbPlMpv, args: Namespace, **kwargs) -> None:
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

    ctr = CliController(db, args)

    if args.read:
        await ctr.choose_play_and_maybe_update(upd=True)
    elif args.readall and args.update:
        await ctr.choose_and_update()
    elif args.readall and args.delete:
        await ctr.choose_and_delete()
    elif args.readall:
        await ctr.choose_play_and_maybe_update(upd=False)
    elif args.update:
        await ctr.update()
    elif args.create:
        db.create(
            entry=args.create,
            collection=args.collection,
            watched=args.watched,
        )
