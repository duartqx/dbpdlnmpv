import subprocess

from argparse import Namespace
from pathlib import Path
from typing import TypeAlias

from persistence.dbplmpv import DbPlMpv
from service import (
    read_all,
    read_filtered,
    update,
)

Rows: TypeAlias = dict[str, dict[str, str | int]]


async def execute_dmenu(input_string: str) -> str:
    process = subprocess.Popen(
        ["dmenu", "-i", "-l", "20"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    output, _ = process.communicate(input=input_string.rstrip("\n").encode())
    return output.decode()


async def play_on_mpv(path: str) -> None:
    subprocess.run(["mpv", "--osc", "--fs", path.strip("\n")])


async def choose_play_and_maybe_update(
    db: DbPlMpv, rows: Rows, upd: bool = True
) -> None:
    chosen: str = await execute_dmenu("\n".join(rows))
    chosen_row: dict[str, str | int] = rows.get(chosen, {})
    if not chosen_row:
        return
    await play_on_mpv(str(chosen_row["path"]))
    if upd:
        await update(db, id=int(chosen_row["id"]))


async def choose_and_update(db: DbPlMpv, rows: Rows) -> str:
    chosen: str = await execute_dmenu("\n".join(rows.keys()).rstrip("\n"))
    chosen_row: dict[str, str | int] = rows.get(chosen.rstrip("\n"), {})
    if not chosen_row:
        return ""
    await update(db, id=int(chosen_row["id"]))
    return chosen


async def cli_handler(db: DbPlMpv, args: Namespace) -> None:
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
        rows: Rows = await read_filtered(db, ctx=args)
        await choose_play_and_maybe_update(db, rows, upd=True)
    elif args.readall and args.update:
        rows: Rows = await read_all(db, withstatus=True)
        print(await choose_and_update(db, rows))
    elif args.readall:
        rows: Rows = await read_all(db, withstatus=args.withstatus)
        await choose_play_and_maybe_update(db, rows, upd=False)
    elif args.update:
        await update(db, id=args.id)
    elif args.create:
        db.create(
            entry=args.create,
            collection=args.collection,
            watched=args.watched,
        )
