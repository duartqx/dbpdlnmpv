from argparse import ArgumentParser, Namespace
from typing import Any


def get_options() -> tuple[dict[str, Any], ...]:
    return (
        {
            "arg": ("-c", "--create"),
            "help": "Create row with the argument passed as title",
            "action": "store",
        },
        {
            "arg": ("-C", "--collection"),
            "help": "Create row that is a collection",
            "action": "store_true",
        },
        {
            "arg": ("-d", "--desc"),
            "help": "Descending order",
            "action": "store_true",
        },
        {
            "arg": ("-i", "--id"),
            "help": "The id of the row",
            "action": "store",
            "type": int,
        },
        {
            "arg": ("-s", "--withstatus"),
            "help": "Print only the title",
            "action": "store_true",
        },
        {
            "arg": ("-r", "--read"),
            "help": "Read one line if id is passed or multiple filtered by watched",
            "action": "store_true",
        },
        {
            "arg": ("-R", "--readall"),
            "help": "Read all lines without a filter",
            "action": "store_true",
        },
        {
            "arg": ("-u", "--update"),
            "help": "Update watched status",
            "action": "store_true",
        },
        {
            "arg": ("-D", "--delete"),
            "help": "Deletes a row from disk and sets it to deleted on the db",
            "action": "store_true",
        },
        {
            "arg": ("-w", "--watched"),
            "help": "Boolean value",
            "action": "store_const",
            "const": 1,
            "default": 0,
        },
    )


def get_cli_args() -> Namespace:
    """
    Builds and returns main's parsed command line arguments

    OPTIONS:
        -c, --create: str -> Title of the row to be created
        -C, --collection -> The entry is a collection/season
        -d, --desc: bool -> Descending order
        -i, --id: int -> Row id
        -s, --withstatus: bool -> Prints row with watched status
        -r, --read: bool -> Reads one line if id is passed or multiple rows by
                            watched status
        -R, --readall: bool -> Reads all rows without filter
        -u, --update: bool -> Updates watched status, requires id to be passed
        -D, --delete: bool -> Deletes from disk and sets deleted in the db
        -w, --watched: const int -> 0 or 1
    """
    parser = ArgumentParser(prog="DbMpv-cli")

    for arg in get_options():
        parser.add_argument(*arg.pop("arg"), **arg)

    args = parser.parse_args()

    checker = sum(
        (
            bool(args.create),
            bool(args.read),
            bool(args.readall),
        )
    )
    if not checker or checker > 1:
        parser.error(
            "Illegal usage: One of --create, --read, --readall, "
            "--choose_update, --update or --delete is required "
            "but they are mutually exclusive."
        )

    if not args.readall and (args.update and not args.id):
        parser.error("--id is required when only updating")

    return args
