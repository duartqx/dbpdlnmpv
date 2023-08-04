from argparse import Namespace
import asyncio
import json
import logging
import os
import sys

from traceback import print_exc
from typing import Any

from persistence.dbplmpv import DbPlMpv
from service import get_coroutine, DbPlMpvCoroutine, DbPlMpvResult


async def fifo_handler(db: DbPlMpv) -> None:
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

    def fd_is_open(fd: int | None) -> bool:
        """Checks if a file descriptor is open/exists"""
        try:
            os.fstat(fd)  # pyright: ignore
            return True
        except:
            return False

    # Log setup
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(levelname)s @ %(asctime)s - %(message)s",
    )

    input_pipe_path: str = "dbmpv_input_fifo"
    output_pipe_path: str = "dbmpv_output_fifo"

    for path in (input_pipe_path, output_pipe_path):
        if os.path.exists(path):
            os.remove(path)
        os.mkfifo(path)

    logging.info(f"LISTENING TO: {input_pipe_path}")
    logging.info(f"WRITING TO: {output_pipe_path}")

    input_pipe_fd = os.open(input_pipe_path, os.O_RDONLY | os.O_NONBLOCK)
    output_pipe_fd: int | None = None

    try:
        while True:
            # Reads from input named pipe
            data: str = os.read(input_pipe_fd, 1024).decode().strip()

            if data:
                logging.info("REQUEST: Received")

            if not data:
                # Sleeps to avoid high cpu usage
                await asyncio.sleep(0.5)
                continue

            try:
                request: dict[str, Any] = json.loads(data)
            except json.JSONDecodeError as e:
                logging.error(f"JSONDecodeError: {e}")
                continue

            command: str = request.get("command", "")

            if not command:
                logging.warning(f"COMMAND: NOT FOUND")
                await asyncio.sleep(0.5)
                continue
            elif command == "exit":
                logging.warning("COMMAND: exit")
                # Breaks out of the inner loop if receives exit
                break

            logging.info(f"COMMAND: {command}")

            context: Namespace = Namespace(**{
                "id": int(request.get("id", -1)),
                "watched": int(request.get("watched", 0)),
                "desc": bool(request.get("desc", 1)),
                "withstatus": bool(request.get("withstatus", 0)),
            })

            coroutine: DbPlMpvCoroutine = get_coroutine(command)

            response: DbPlMpvResult = await coroutine(db, context)

            if response:
                # Writes the response to the output pipe
                logging.info(
                    f"RESPONSE: Read {output_pipe_path} "
                    f"for result of '{command}' "
                )
                try:
                    output_pipe_fd = os.open(output_pipe_path, os.O_WRONLY)

                    os.write(output_pipe_fd, str(response).encode())

                    await asyncio.sleep(0.5)
                finally:
                    if output_pipe_fd is not None and fd_is_open(
                        output_pipe_fd
                    ):
                        os.close(output_pipe_fd)

            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        pass
    except:
        print_exc()
    finally:
        logging.info(f"CLOSING PIPES: {input_pipe_path} / {output_pipe_path}")

        # Closes the input and output named pipes
        if fd_is_open(input_pipe_fd):
            os.close(input_pipe_fd)
        if output_pipe_fd is not None and fd_is_open(output_pipe_fd):
            os.close(output_pipe_fd)

        for path in (input_pipe_path, output_pipe_path):
            os.remove(path)
