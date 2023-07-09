#!/usr/bin/env python
from argparse import ArgumentParser, Namespace
from pathlib import Path
from traceback import print_exc
from typing import Any, Callable, Coroutine, TypeAlias, Union

import asyncio
import json
import os

from cli_args import get_args
from dbplmpv import DbPlMpv, get_connection


FifoContext: TypeAlias = dict[str, Union[int, bool, str]]
FifoCoroutine: TypeAlias = Callable[[dict[str, Any]], Coroutine[Any, Any, str]]


DB: DbPlMpv = get_connection()


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


def format_row(row: Namespace, withstatus: bool) -> str:
    suffix: str = " [WATCHED]\n" if (row.watched and withstatus) else "\n"
    return f"{row.id} - {row.title}{suffix}"


async def read_filtered(ctx: Namespace) -> str:
    """
    Reads the database for a single row with it's id, if it's present on the
    context or all rows filtered by the watched status
    """
    if ctx.id and ctx.id > 0:
        # Queries for the row with the id passed on the context
        row: Namespace = Namespace(**DB.read_one(id=int(ctx.id)))
        if row._get_kwargs():
            # Formats the row string and writes to the output pipe file
            # descriptor
            return format_row(row, withstatus=ctx.withstatus)
    return "".join(
        [
            format_row(Namespace(**row), withstatus=ctx.withstatus)
            for row in DB.read_filtered(watched=ctx.watched, desc=ctx.desc)
        ]
    )


async def read_all(withstatus: bool) -> str:
    """Reads all rows in the database and returns the formated string"""
    return "".join(
        [
            format_row(Namespace(**row), withstatus=withstatus)
            for row in DB.read_all()
        ]
    )


async def update(id: int) -> None:
    """Updates the watched column on a single row based on it's id"""
    if id > 0:
        DB.update_watched(id=id)


async def cli(args: Namespace) -> None:
    args.watched = int(args.watched)

    # Checks if the video file still exists in the playlist folder, if not
    # then updates its row to deleted=1
    if args.read or args.readall:
        DB.delete(
            tuple(
                (
                    int(row["id"])
                    for row in DB.read_all()
                    if not Path(f"{row['path']}").is_file()
                )
            )
        )

    if args.read:
        print((await read_filtered(ctx=args)).rstrip("\n"))
    elif args.readall:
        print((await read_all(withstatus=args.withstatus)).rstrip("\n"))
    elif args.update:
        await update(id=args.id)
    elif args.create:
        DB.create(
            entry=args.create,
            collection=args.collection,
            watched=args.watched,
        )


async def fifo_read_filtered(context: FifoContext) -> str:
    """Calls read_filtered after converting context to Namespace"""
    return await read_filtered(Namespace(**context))


async def fifo_read_all(context: FifoContext) -> str:
    """Reads all rows in the database and returns a formated string"""
    return await read_all(withstatus=bool(context["withstatus"]))


async def fifo_update(context: FifoContext) -> str:
    """
    Calls update and tries to update a row based on it's id, only updates a
    row if the id is bigger than 0
    """
    await update(id=int(context.get("id", -1)))
    return ""


async def blank(context: FifoContext) -> str:
    return ""


def get_coroutine(command: str) -> FifoCoroutine:
    callback_dict = {
        "read": fifo_read_filtered,
        "readall": fifo_read_all,
        "update": fifo_update,
    }
    return callback_dict.get(command, blank)


def fd_is_open(fd: int | None) -> bool:
    """Checks if a file descriptor is open/exists"""
    if fd is None:
        return False
    try:
        os.fstat(fd)
        return True
    except:
        pass
    return False


async def listen() -> None:
    """
    Starts a fifo named pipe and keeps listening for commands coming from it
    while also writing to another pipe that needs to be read from

    listen will wait for requests to be sent to the input pipe and parse
    the request and if a command is found, then it will call the approppriate
    function for it.

    A request is a json object that looks like this one and needs to be piped to
    the input pipe:
        {
            "command": "read",
            "id": 22,
            "watched": 1,
            "desc": 1,
            "withstatus": 1
        }
    """
    input_pipe_path: str = "dbmpv_input_fifo"
    output_pipe_path: str = "dbmpv_output_fifo"

    for path in (input_pipe_path, output_pipe_path):
        if os.path.exists(path):
            os.remove(path)
        os.mkfifo(path)

    print(f"Started listening to: {input_pipe_path}")
    print(f"Writing to: {output_pipe_path}")

    input_pipe_fd = os.open(input_pipe_path, os.O_RDONLY | os.O_NONBLOCK)
    output_pipe_fd: int | None = None

    try:
        while True:
            # Reads from input named pipe
            data: str = os.read(input_pipe_fd, 1024).decode().strip()

            if data:
                print("Received a command, parsing it...")

            if not data:
                # Sleeps to avoid high cpu usage
                await asyncio.sleep(0.5)
                continue

            if "exit" in data:
                # Breaks out of the inner loop if receives exit
                break

            try:
                request: dict[str, Any] = json.loads(data)
            except json.JSONDecodeError:
                print("Json Decode Error, still listening...")
                continue

            command: str = request.get("command", "")

            if command:
                print(f"Received command: {command}")
            else:
                print(f"No command found in the request")
                await asyncio.sleep(0.5)
                continue

            context: FifoContext = {
                "id": int(request.get("id", -1)),
                "watched": int(request.get("watched", 0)),
                "desc": bool(request.get("desc", 1)),
                "withstatus": bool(request.get("withstatus", 0)),
            }

            coroutine: FifoCoroutine = get_coroutine(command)

            response: str = await coroutine(context)

            if response:
                # Writes the response to the output pipe
                print(
                    f"Writing the response of '{command}' "
                    f"to the output pipe {output_pipe_path}"
                )
                try:
                    output_pipe_fd = os.open(output_pipe_path, os.O_WRONLY)

                    os.write(output_pipe_fd, response.encode())

                    await asyncio.sleep(0.5)
                finally:
                    if output_pipe_fd is not None and fd_is_open(output_pipe_fd):
                        os.close(output_pipe_fd)

            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        pass
    except:
        print_exc()
    finally:
        print(
            f"Exit code: Closing Named Pipes "
            f"{input_pipe_path} and {output_pipe_path}"
        )

        # Closes the input and output named pipes
        if fd_is_open(input_pipe_fd):
            os.close(input_pipe_fd)
        if output_pipe_fd is not None and fd_is_open(output_pipe_fd):
            os.close(output_pipe_fd)

        for path in (input_pipe_path, output_pipe_path):
            os.remove(path)


async def main() -> None:
    args: Namespace = _get_args()

    with DB.conn:
        if args.fifo:
            await listen()
        else:
            await cli(args)


if __name__ == "__main__":
    asyncio.run(main())
