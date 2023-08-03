#!/usr/bin/env bash
# shellcheck disable=SC2086

DMENU_OPTIONS='Watch
Update
Watched
Add'

Choice=$(echo "$DMENU_OPTIONS" | dmenu -i)

[[ -z $Choice ]] && exit

case "$Choice" in
Watch)
    dbmpv --read
    ;;
Update)
    _updated=$(dbmpv --choose_update)
    if [[ -n $_updated ]]; then
        notify-send "Updated watched status for $_updated"
    fi
    dbanimeplaylist
    ;;
Watched)
    dbmpv --read --watched --desc
    ;;
Add)
    CLIP=$(xclip -selection clipboard -o 2>/dev/null)
    [[ -n $CLIP ]] && dbmpv --create "$CLIP"
    ;;
esac
