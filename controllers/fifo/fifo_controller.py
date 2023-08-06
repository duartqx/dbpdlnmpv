from argparse import Namespace
from typing import Any, Callable, Coroutine, TypeAlias

from persistence.dbplmpv import DbPlMpv
from .cli_service import read_filtered, read_all, update, DbPlMpvResult

DbPlMpvCoroutine: TypeAlias = Callable[
    [DbPlMpv, Namespace], Coroutine[Any, Any, DbPlMpvResult]
]


async def blank(db: DbPlMpv, ctx: Namespace) -> DbPlMpvResult:
    return {}


COROUTINE_DICT: dict[str, DbPlMpvCoroutine] = {
    "read": read_filtered,
    "readall": read_all,
    "update": update,
}


def get_coroutine(command: str) -> DbPlMpvCoroutine:
    return COROUTINE_DICT.get(command, blank)
