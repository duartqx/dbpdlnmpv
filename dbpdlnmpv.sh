#!/usr/share/env bash

DB_FILE="--db_file '/home/duartqx/.local/share/playlists.db'"
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
        dbpdlnmpv_create $DB_FILE $TABLE_NAME --title "$2" ;;
    "-u"|"--update")
        if [[ -z "$2" ]]; then
            echo 'Missing argument'; exit 1
        fi
        dbpdlnmpv_update $DB_FILE $TABLE_NAME --id "$2" ;;
    "-r"|"--read")
        if [[ -z "$2" ]]; then
            dbpdlnmpv_read $DB_FILE $TABLE_NAME --id "$2" ;;
        fi
            dbpdlnmpv_read $DB_FILE $TABLE_NAME ;;
esac
