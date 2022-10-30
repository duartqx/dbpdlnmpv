#!/usr/bin/env bash

DBCREATOR="$HOME/.local/bin/repos/dbpdlnmpv/create.py"
DBUPDATER="$HOME/.local/bin/repos/dbpdlnmpv/update.py"
DBREADER="$HOME/.local/bin/repos/dbpdlnmpv/read.py"
DB_FILE="--db_file /home/duartqx/.local/share/playlists.db"

if [[ $1 == '--table' ]]; then
    if [[ -z $2 ]]; then
        echo 'Missing argument'; exit 1
    fi
    TABLE_NAME="--table_name $2"
else
    echo 'Missing argument'; exit 1
fi

shift; shift 

case $1 in
    "-c"|"--create")
        if [[ -z "$2" ]]; then
            echo 'Missing argument'; exit 1
        fi
        echo "$2"
        $DBCREATOR $DB_FILE $TABLE_NAME --title "$2" ;;
    "-u"|"--update")
        if [[ -z "$2" ]]; then
            echo 'Missing argument'; exit 1
        fi
        $DBUPDATER $DB_FILE $TABLE_NAME --id "$2" ;;
    "-r"|"--read")
        if [[ -z "$2" ]]; then
            $DBREADER $DB_FILE $TABLE_NAME --id "$2"
        else
            $DBREADER $DB_FILE $TABLE_NAME
        fi ;;
esac
