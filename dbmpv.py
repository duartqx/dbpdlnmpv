#!/usr/bin/env python
from argparse import ArgumentParser, Namespace
from cli_args import get_args
from dbplmpv import DbPlMpv
from pathlib import Path

import json
import os


class ConfigFileNotFoundError(Exception):
    pass


def _get_connection() -> DbPlMpv:
    CONFIG_FILE: str = f"{os.environ['HOME']}/.config/dbmpv.json"
    if not Path(CONFIG_FILE).is_file():
        raise ConfigFileNotFoundError(
            "You need to have the config file with keys DB_FILE, "
            "TABLE_NAME and COLLECTION_TABLE_NAME"
        )
    with open(CONFIG_FILE, "r") as config_fh:
        config: Namespace = Namespace(**json.load(config_fh))

    return DbPlMpv(
        table_name=config.TABLE_NAME,
        collection_table_name=config.COLLECTION_TABLE_NAME,
        db_file=config.DB_FILE,
    )


def _get_args() -> Namespace:
    """
    Builds and returns main's parsed command line arguments

    OPTIONS:
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


def main() -> None:
    args: Namespace = _get_args()

    db: DbPlMpv = _get_connection()

    with db.conn:
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
                    for row in db.read_filtered(
                        watched=watched, desc=args.desc
                    )
                ]
                for row in rows:
                    formatted_row: str = f"{row.id} - {row.title}"
                    if args.withstatus:
                        formatted_row += " [WATCHED]" if row.watched else ""
                    print(formatted_row)
        elif args.readall:
            rows: list[Namespace] = [
                Namespace(**row)
                for row in db.read_all()
            ]
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


if __name__ == "__main__":
    main()
