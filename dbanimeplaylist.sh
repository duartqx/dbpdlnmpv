#!/usr/bin/env bash
# shellcheck disable=SC2086

DMENU_OPTIONS='Watch
Watch Collection
Update
Watched
Add'

DB_FILE="$HOME/.local/share/playlists.db"
TABLE_NAME='animeplaylist'

Choice=$(echo "$DMENU_OPTIONS" | dmenu -i)

[[ -z $Choice ]] && exit

case "$Choice" in
Watch)
    _choice=$(dbmpv $DB_FILE $TABLE_NAME --read | dmenu -i -l 20)

    # Exits if no choice was selected
    [[ -z $_choice ]] && exit

    # Plays the file in fullscreen
    mpv --fs "$WATCH_FOLDER/${_choice#*- }"

    # Sets the file to watched
    dbmpv $DB_FILE $TABLE_NAME -u --id "${_choice%%-*}"
    ;;
Update)
    _to_update=$(dbmpv $DB_FILE $TABLE_NAME --readall | dmenu -i -l 20)

    # Exits if no choice was selected
    [[ -z $_to_update ]] && exit

    # Update
    dbmpv $DB_FILE $TABLE_NAME --update --id "${_to_update%%-*}"
    notify-send "Updated watched status for $_to_update"
    dbanimeplaylist
    ;;
Watched)
    _choice=$(dbmpv $DB_FILE $TABLE_NAME --read --watched --desc | dmenu -i -l 20)

    # Exits if no choice was selected
    [[ -z $_choice ]] && exit

    # Plays the file in fullscreen
    mpv --fs "$WATCH_FOLDER/${_choice#*- }"
    ;;
Add)
    CLIP=$(xclip -selection clipboard -o 2>/dev/null)
    [[ -n $CLIP ]] && dbmpv $DB_FILE $TABLE_NAME --create "$CLIP"
    ;;
esac
