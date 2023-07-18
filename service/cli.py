from argparse import Namespace

from persistence.dbplmpv import DbPlMpv


def format_row(row: Namespace, withstatus: bool) -> str:
    suffix: str = " [WATCHED]\n" if (row.watched and withstatus) else "\n"
    return f"{row.id} - {row.title}{suffix}"


async def read_filtered(db: DbPlMpv, ctx: Namespace) -> str:
    """
    Reads the database for a single row with it's id, if it's present on the
    context or all rows filtered by the watched status
    """
    if ctx.id and ctx.id > 0:
        # Queries for the row with the id passed on the context
        row: Namespace = Namespace(**db.read_one(id=int(ctx.id)))
        if row._get_kwargs():
            # Formats the row string and writes to the output pipe file
            # descriptor
            return format_row(row, withstatus=ctx.withstatus)
    return "".join(
        [
            format_row(Namespace(**row), withstatus=ctx.withstatus)
            for row in db.read_filtered(watched=ctx.watched, desc=ctx.desc)
        ]
    )


async def read_all(db: DbPlMpv, withstatus: bool) -> str:
    """Reads all rows in the database and returns the formated string"""
    return "".join(
        [
            format_row(Namespace(**row), withstatus=withstatus)
            for row in db.read_all()
        ]
    )


async def update(db: DbPlMpv, id: int) -> None:
    """Updates the watched column on a single row based on it's id"""
    if id > 0:
        db.update_watched(id=id)
