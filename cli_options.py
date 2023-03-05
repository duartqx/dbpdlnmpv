from typing import Any


def get_options() -> tuple[dict[str, Any], ...]:
    return (
        {
            "arg": "dbfile",
            "help": "The sqlite database file to be read. required",
        },
        {
            "arg": "table",
            "help": "The table name on the dbfile. required",
        },
        {
            "opt": "-c",
            "flag": "--create",
            "help": "Create row with the argument passed as title",
            "action": "store",
        },
        {
            "opt": "-d",
            "flag": "--desc",
            "help": "Descending order",
            "action": "store_true",
        },
        {
            "opt": "-i",
            "flag": "--id",
            "help": "The id of the row",
            "action": "store",
            "type": int,
        },
        {
            "opt": "-n",
            "flag": "--nostatus",
            "help": "Print only the title",
            "action": "store_true",
        },
        {
            "opt": "-p",
            "flag": "--path",
            "help": "The folder where the video files are stored. required",
        },
        {
            "opt": "-r",
            "flag": "--read",
            "help": "Read one line if id is passed or multiple filtered by watched",
            "action": "store_true",
        },
        {
            "opt": "-R",
            "flag": "--readall",
            "help": "Read all lines without a filter",
            "action": "store_true",
        },
        {
            "opt": "-u",
            "flag": "--update",
            "help": "Update watched status",
            "action": "store_true",
        },
        {
            "opt": "-w",
            "flag": "--watched",
            "help": "Boolean value",
            "action": "store_true",
        },
    )
