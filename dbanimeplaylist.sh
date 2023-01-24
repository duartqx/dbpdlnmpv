#!/usr/bin/env bash
# shellcheck disable=SC2086

DMENU_OPTIONS='Watch
Update
Watched
Add'

#DB_FILE="$HOME/.local/share/playlists.db"
TABLE_NAME='--table animeplaylist'
WATCH_FOLDER="$HOME/Media/Videos"

Choice=$(echo "$DMENU_OPTIONS" | dmenu -i)

[[ -z $Choice ]] && exit

case "$Choice" in
    Watch)
        Watch_choice=$(dbmpv $TABLE_NAME --read | dmenu -i -l 20)
        [[ -z $Watch_choice ]] && exit
        mpv --fs "$WATCH_FOLDER/${Watch_choice#*- }"
        # Sets the file to watched
        _id=${Watch_choice%%-*} # Removes everything and leaves only the id
        dbmpv $TABLE_NAME --update --id "$_id" --watched 1
    ;;
    Update)
        What_entry_to_update=$(dbmpv $TABLE_NAME --readall | dmenu -i -l 20)
        [[ -z $What_entry_to_update ]] && exit
        _id=${What_entry_to_update%%-*} # Removes everything and leaves only the id
        dbmpv $TABLE_NAME --update --id "$_id"
        notify-send "Updated watched status for $What_entry_to_update"
        dbanimeplaylist
    ;;
    Watched)
        Watch_choice=$(dbmpv $TABLE_NAME --read --watched 1 --desc | dmenu -i -l 20)
        [[ -z $Watch_choice ]] && exit
        mpv --fs "$WATCH_FOLDER/${Watch_choice#*- }"
    ;;
    Add)
        CLIP=$(xclip -selection clipboard -o 2>/dev/null)
        dbmpv $TABLE_NAME --create "$CLIP"
    ;;
esac
