from argparse import Namespace
from typing import Any, TypeAlias

from persistence.dbplmpv import DbPlMpv

DbPlMpvResult: TypeAlias = dict[str, dict[str, Any]]


def format_row(row: dict[str, Any], withstatus: bool) -> str:
    suffix: str = " [WATCHED]" if (row["watched"] and withstatus) else ""
    return f"{row['id']} - {row['title']}{suffix}"


async def read_filtered(db: DbPlMpv, ctx: Namespace) -> DbPlMpvResult:
    """
    Reads the database for a single row with it's id, if it's present on the
    context or all rows filtered by the watched status
    """
    if ctx.id and ctx.id > 0:
        # Queries for the row with the id passed on the context
        row: dict[str, str | int] = db.read_one(id=int(ctx.id))
        if row:
            # Formats the row string and writes to the output pipe file
            # descriptor
            return {format_row(row, withstatus=ctx.withstatus): row}
    return {
        format_row(row, withstatus=ctx.withstatus): row
        for row in db.read_filtered(watched=ctx.watched, desc=ctx.desc)
    }


async def read_all(db: DbPlMpv, ctx: Namespace) -> DbPlMpvResult:
    """Reads all rows in the database and returns the formated string"""
    return {
        format_row(row, withstatus=ctx.withstatus): row
        for row in db.read_all()
    }


async def update(db: DbPlMpv, ctx: Namespace) -> DbPlMpvResult:
    """Updates the watched column on a single row based on it's id"""
    if ctx.id > 0:
        db.update_watched(id=ctx.id)
    return {}
