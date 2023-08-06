import os

from argparse import Namespace
from typing import Any, TypeAlias, Union

from persistence.dbplmpv import DbPlMpv
from exec.exec import execute_dmenu, execute_notify_send, execute_mpv

DbPlMpvResult: TypeAlias = dict[str, dict[str, Any]]
Row: TypeAlias = dict[str, str | int]
Rows: TypeAlias = dict[str, Row]


class Service:
    def __init__(self, db: DbPlMpv, ctx: Namespace) -> None:
        self.db = db
        self.ctx = ctx

    def format_row(self, row: Row) -> str:
        suffix: str = (
            " [WATCHED]" if (row["watched"] and self.ctx.withstatus) else ""
        )
        return f"{row['id']} - {row['title']}{suffix}"

    async def read_filtered(self, **kwargs) -> DbPlMpvResult:
        """
        Reads the database for a single row with it's id, if it's present on the
        context or all rows filtered by the watched status
        """
        if self.ctx.id and self.ctx.id > 0:
            # Queries for the row with the id passed on the context
            row: Row = self.db.read_one(id=int(self.ctx.id))
            if row:
                # Formats the row string and writes to the output pipe file
                # descriptor
                return {self.format_row(row): row}
        return {
            self.format_row(row): row
            for row in self.db.read_filtered(
                watched=self.ctx.watched, desc=self.ctx.desc
            )
        }

    async def read_all(self, **kwargs) -> DbPlMpvResult:
        """Reads all rows in the database and returns the formated string"""
        return {self.format_row(row): row for row in self.db.read_all()}

    async def update(self, **kwargs) -> DbPlMpvResult:
        """Updates the watched column on a single row based on it's id"""
        if self.ctx.id > 0:
            self.db.update_watched(id=self.ctx.id)
        return {}

    async def choose_row(self, **kwargs) -> Row:
        rows: Rows = await self.read_filtered()
        chosen: str = await execute_dmenu("\n".join(rows))
        if not chosen:
            exit()
        row: Row = rows.get(chosen, {})
        if not row:
            await execute_notify_send(
                "Something went wrong and the row could not be located!"
            )
            exit(1)
        return row

    async def choose_play_and_maybe_update(self, **kwargs) -> None:
        chosen_row: Row = await self.choose_row()
        await execute_mpv(str(chosen_row["path"]))
        if kwargs.get("upd") and int(chosen_row["id"]):
            self.db.update_watched(id=int(chosen_row["id"]))

    async def choose_and_update(self, **kwargs) -> None:
        chosen_row: Row = await self.choose_row()
        self.db.update_watched(id=int(chosen_row["id"]))
        await execute_notify_send(
            f"Updated watched status for {chosen_row['title']}"
        )

    async def choose_and_delete(self, **kwargs) -> None:
        chosen_row: Union[Row, None] = await self.choose_row()
        ask_confirmation_of_deletion: str = await execute_dmenu(
            "Yes\nNo",
            cmd=(
                "dmenu",
                "-i",
                "-p",
                f"Continue and DELETE '{chosen_row['title']}'?",
            ),
        )
        if (
            not ask_confirmation_of_deletion
            or ask_confirmation_of_deletion == "No"
        ):
            exit()
        try:
            os.remove(str(chosen_row["path"]))
            self.db.delete((int(chosen_row["id"]),))
            await execute_notify_send(
                f"'{chosen_row['title']}' has been successfully deleted."
            )
        except (FileNotFoundError, PermissionError):
            await execute_notify_send(
                f"'{chosen_row['title']}' could not be deleted."
            )
