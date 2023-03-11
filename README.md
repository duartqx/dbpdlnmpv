![dbpdlnmpv](https://github.com/duartqx/images/blob/main/dbpdlnmpv.png?raw=true "dbpdlnmpv")

# dbpdlnmpv - Database: Playlist Download and mpv

dbpdlnmpv is an evolution of [pdlnmpv](https://github.com/duartqx/pdlnlink/blob/main/pdlnmpv) that uses a [sqlite](https://docs.python.org/3/library/sqlite3.html) database to manage local playlists in conjunction with [dmenu](https://tools.suckless.org/dmenu/). Dmenu is a straightforward tool for creating simple menus. Simply pipe something into it, and it will display as a menu on the screen. It is used in this case to show the user read and select operations.

All of these script files interact as follows:

 1. dbplnmpv.py is in charge of all database operations such as create, read, update, and delete.
 2. dbmpv.py is in charge of interacting with dbplnmpv.py via a simple, straightforward command-line interface.
 3. dbanimeplaylist.sh is a bash script that runs dbmpv and outputs the results to dmenu. This is the main interface, which can be accessed via keybindings or a.desktop file on GNU/Linux. Before you can use it, you must change the three variables at the top: DB FILE, TABLE NAME, and WATCH FOLDER to something you prefer. If DB FILE or TABLE NAME does not exist, dbplnmpv.py will create it for you.
