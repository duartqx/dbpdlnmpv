#!/usr/bin/env bash

DMENU_OPTIONS='Watch
Update
Watched
Add'

#DB_FILE="$HOME/.local/share/playlists.db"
TABLE_NAME='--table animeplaylist'
WATCH_FOLDER="$HOME/Media/Videos"

Choice=$(echo "$DMENU_OPTIONS" | dmenu -i)

checkIfDeleted() {
    allFiles=$(dbmpv $TABLE_NAME --read)
    while IFS= read -r file; do
        if [[ -z $(ls "$WATCH_FOLDER/${file#*- }" 2>/dev/null) ]]; then
            deletedFiles="$deletedFiles ${file%% -*}"
        fi
    done <<< "$allFiles"
    dbmpv $TABLE_NAME --deleted "$deletedFiles"
}

checkIfDeleted

[[ -z $Choice ]] && exit

case "$Choice" in
    Watch)
        Watch_choice=$(dbmpv $TABLE_NAME --read | dmenu -l 10)
        Filename=${Watch_choice#*- }
        _id=${Watch_choice%%-*} # Removes everything and leaves only the id
        cd "$WATCH_FOLDER" || exit
        mpv --fs "$Filename"
        # Sets the file to watched
        dbmpv "$TABLE_NAME" --update --id "$_id" --watched 1
    ;;
    Update)
        Update_choice=$(echo -e "Watched\nUnwatched" | dmenu -i -p "Update to what state? ")
        [[ -z $Update_choice ]] && exit
        case "$Update_choice" in
            Watched)
                WBool=1 ;;
            Unwatched)
                WBool=0 ;;
        esac
        What_entry_to_update=$(dbmpv $TABLE_NAME --readall | dmenu -l 10)
        _id=${What_entry_to_update%%-*} # Removes everything and leaves only the id
        dbmpv $TABLE_NAME --update --id "$_id" --watched $WBool
        notify-send "Changed file state to $Update_choice"
    ;;
    Watched)
        Watch_choice=$(dbmpv $TABLE_NAME --read --watched 1 | dmenu -l 10)
    ;;
    Add)
        CLIP=$(xclip -selection clipboard -o 2>/dev/null)
        dbmpv "$TABLE_NAME" --create "$CLIP"
    ;;
esac
