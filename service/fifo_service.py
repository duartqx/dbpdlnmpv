from argparse import Namespace
from typing import Any, Callable, Coroutine, TypeAlias, Union

from persistence.dbplmpv import DbPlMpv
from .cli_service import read_filtered, read_all, update

FifoContext: TypeAlias = dict[str, Union[int, bool, str]]
FifoCoroutine: TypeAlias = Callable[
    [DbPlMpv, FifoContext], Coroutine[Any, Any, str]
]


async def fifo_read_filtered(db: DbPlMpv, context: FifoContext) -> str:
    """Calls read_filtered after converting context to Namespace"""
    return "\n".join(await read_filtered(db, Namespace(**context)))


async def fifo_read_all(db: DbPlMpv, context: FifoContext) -> str:
    """Reads all rows in the database and returns a formated string"""
    return "\n".join(
        await read_all(db, withstatus=bool(context.get("withstatus")))
    )


async def fifo_update(db: DbPlMpv, context: FifoContext) -> str:
    """
    Calls update and tries to update a row based on it's id, only updates a
    row if the id is bigger than 0
    """
    await update(db, id=int(context.get("id", -1)))
    return ""


async def blank(db: DbPlMpv, context: FifoContext) -> str:
    return ""


COROUTINE_DICT: dict[str, FifoCoroutine] = {
    "read": fifo_read_filtered,
    "readall": fifo_read_all,
    "update": fifo_update,
}


def get_coroutine(command: str) -> FifoCoroutine:
    return COROUTINE_DICT.get(command, blank)
