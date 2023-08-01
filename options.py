from typing import Any


def get_options() -> tuple[dict[str, Any], ...]:
    return (
        {
            "arg": ("-f", "--fifo"),
            "help": "Starts the script in fifo mode and keeps listening to commands",
            "action": "store_true",
        },
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
            "arg": ("-w", "--watched"),
            "help": "Boolean value",
            "action": "store_true",
        },
    )
