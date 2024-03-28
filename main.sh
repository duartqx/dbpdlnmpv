#!/usr/bin/env bash
# shellcheck disable=SC2086

Choice=$(echo -e "Watch\nUpdate\nWatched\nDelete\nPurge\nAdd" | dmenu -i)

[[ -z $Choice ]] && exit

case "$Choice" in
Watch)
    dbmpv --read
    ;;
Update)
    dbmpv --readall --update --withstatus
    ;;
Watched)
    dbmpv --read --watched --desc
    ;;
Delete)
    dbmpv --readall --delete --desc
    ;;
Purge)
    dbmpv --purge
    ;;
Add)
    CLIP=$(xclip -selection clipboard -o 2>/dev/null)
    [[ -n $CLIP ]] && dbmpv --create "$CLIP"
    ;;
esac
