import json

from .dbplmpv import *

CONFIG_NOT_FOUND_MSG: str = """$HOME/.config/dbmpv.json not found!

Sample config:

    {
        "BASE_PATH": "$HOME/Videos",
        "DB_FILE": "$HOME/.config/mydb.db",
        "TABLE_NAME": "mymaintable",
        "COLLECTION_TABLE_NAME": "mycollectiontablename"
    }

"""


def get_connection(config: str) -> DbPlMpv:
    class ConfigFileNotFoundError(Exception):
        pass

    if not Path(config).is_file():
        raise ConfigFileNotFoundError(CONFIG_NOT_FOUND_MSG)
    with open(config, "r") as config_fh:
        return DbPlMpv(config=Namespace(**json.load(config_fh)))
