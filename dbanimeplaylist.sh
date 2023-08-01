#!/usr/bin/env bash
# shellcheck disable=SC2086

WATCH_FOLDER="$HOME/Media/Videos"
DMENU_OPTIONS='Watch
Update
Watched
Add'

Choice=$(echo "$DMENU_OPTIONS" | dmenu -i)

[[ -z $Choice ]] && exit

case "$Choice" in
Watch)
    _choice=$(dbmpv --read | dmenu -i -l 20)

    # Exits if no choice was selected
    [[ -z $_choice ]] && exit

    # Plays the file in fullscreen
    mpv --fs "$WATCH_FOLDER/${_choice#*- }"

    # Sets the file to watched
    dbmpv --update --id "${_choice%%-*}"
    ;;
Update)
    _to_update=$(dbmpv --readall --withstatus | dmenu -i -l 20)

    # Exits if no choice was selected
    [[ -z $_to_update ]] && exit

    # Update
    dbmpv --update --id "${_to_update%%-*}"
    notify-send "Updated watched status for $_to_update"
    dbanimeplaylist
    ;;
Watched)
    _choice=$(dbmpv --read --watched --desc | dmenu -i -l 20)

    # Exits if no choice was selected
    [[ -z $_choice ]] && exit

    # Plays the file in fullscreen
    mpv --fs "$WATCH_FOLDER/${_choice#*- }"
    ;;
Add)
    CLIP=$(xclip -selection clipboard -o 2>/dev/null)
    [[ -n $CLIP ]] && dbmpv --create "$CLIP"
    ;;
esac
