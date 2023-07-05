#!/usr/bin/env python
from argparse import ArgumentParser, Namespace
from cli_args import get_args
from dbplmpv import DbPlMpv, get_connection
from pathlib import Path
from typing import Any, Callable, Coroutine, Union

import asyncio
import json
import os


db: DbPlMpv = get_connection()


def _get_args() -> Namespace:
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

    for arg in get_args():
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


async def cli(args: Namespace) -> None:
    watched = int(args.watched)

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
        if args.id:
            row = db.read_one(id=args.id)
            if row:
                print(Namespace(**row))
        else:
            rows: list[Namespace] = [
                Namespace(**row)
                for row in db.read_filtered(watched=watched, desc=args.desc)
            ]
            for row in rows:
                formatted_row: str = f"{row.id} - {row.title}"
                if args.withstatus:
                    formatted_row += " [WATCHED]" if row.watched else ""
                print(formatted_row)
    elif args.readall:
        rows: list[Namespace] = [Namespace(**row) for row in db.read_all()]
        for row in rows:
            formatted_row: str = f"{row.id} - {row.title}"
            if args.withstatus:
                formatted_row += " [WATCHED]" if row.watched else ""
            print(formatted_row)
    elif args.update:
        db.update_watched(id=args.id)
    else:
        db.create(
            entry=args.create,
            collection=args.collection,
            watched=watched,
        )


async def fifo_read(
    output_pipe_fd: int, context: dict[str, Union[int, bool, str]]
) -> None:
    ctx: Namespace = Namespace(**context)
    if ctx.id != -1:
        # Queries for the row with the id passed on the context
        row: Namespace = Namespace(**db.read_one(id=int(ctx.id)))
        if row._get_kwargs():
            # Formats the row string and writes to the output pipe file
            # descriptor

            formatted_row: str = f"{row.id} - {row.title}"
            if context["withstatus"]:
                formatted_row += " [WATCHED]" if row.watched else ""

            # Writes to the fifo
            os.write(output_pipe_fd, formatted_row.encode())
    else:
        rows: list[Namespace] = [
            Namespace(**row)
            for row in db.read_filtered(watched=ctx.watched, desc=ctx.desc)
        ]
        formatted_rows: list[str] = []
        for row in rows:
            formatted_row: str = f"{row.id} - {row.title}"
            if ctx.withstatus:
                formatted_row += " [WATCHED]" if row.watched else ""
            formatted_rows.append(formatted_row)

        # Writes to the fifo
        os.write(output_pipe_fd, "\n".join(formatted_rows).encode())


async def blank(
    output_pipe_fd: int, context: dict[str, Union[int, bool, str]]
) -> None:
    pass


def get_callback(
    command: str,
) -> Callable[
    [int, dict[str, Union[int, bool, str]]], Coroutine[Any, Any, None]
]:
    callback_dict: dict[
        str,
        Callable[
            [int, dict[str, Union[int, bool, str]]], Coroutine[Any, Any, None]
        ],
    ] = {
        "read": fifo_read,
    }
    return callback_dict.get(command, blank)


async def listen() -> None:
    """
    Starts a fifo named pipe and keeps listening for commands coming from it
    while also writing to another pipe that needs to be read from
    """
    input_pipe_path: str = "dbmpv_input_fifo"
    output_pipe_path: str = "dbmpv_output_fifo"

    if not os.path.exists(input_pipe_path):
        os.mkfifo(input_pipe_path)

    if not os.path.exists(output_pipe_path):
        os.mkfifo(output_pipe_path)

    input_pipe_fd: int = os.open(input_pipe_path, os.O_RDONLY | os.O_NONBLOCK)
    output_pipe_fd: int = os.open(output_pipe_path, os.O_WRONLY)

    try:
        print(f"Started listening at: {input_pipe_path}")
        print(f"Writing to: {output_pipe_path}")
        while True:
            # Reads from input named pipe
            data: str = os.read(input_pipe_fd, 1024).decode().strip()

            if not data:
                # Sleeps to avoid high cpu usage
                await asyncio.sleep(0.5)
                continue

            if data == "exit":
                break

            request: dict[str, str] = json.loads(data)

            # request example:

            # {
            #    "command": "read",
            #    "id": 22,
            #    "watched": 1,
            #    "desc": 1,
            #    "withstatus": 1
            # }

            command: str = request.get("command", "")

            context: dict[str, Union[int, bool, str]] = {
                "id": int(request.get("id", -1)),
                "watched": int(request.get("watched", 0)),
                "desc": bool(request.get("desc", 1)),
                "withstatus": bool(request.get("withstatus", 0)),
            }

            callback: Callable[
                [int, dict[str, Union[int, bool, str]]],
                Coroutine[Any, Any, None],
            ] = get_callback(command)

            await callback(output_pipe_fd, context)

            await asyncio.sleep(0.5)
    except:
        import traceback

        traceback.print_exc()
    finally:
        print("Exit code")
        # Close the input and output named pipes
        os.close(input_pipe_fd)
        os.close(output_pipe_fd)

        # Remove the named pipes
        os.remove(input_pipe_path)
        os.remove(output_pipe_path)


async def main() -> None:
    args: Namespace = _get_args()

    with db.conn:
        await listen() if args.fifo else cli(args)


if __name__ == "__main__":
    asyncio.run(main())
