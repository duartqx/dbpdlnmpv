![dbpdlnmpv](https://github.com/duartqx/images/blob/main/dbpdlnmpv.png?raw=true "dbpdlnmpv")

# dbpdlnmpv - Database: Playlist Download and mpv

dbpdlnmpv is an evolution of [pdlnmpv](https://github.com/duartqx/pdlnlink/blob/main/pdlnmpv) that uses a [sqlite](https://docs.python.org/3/library/sqlite3.html) database to manage local playlists in conjunction with [dmenu](https://tools.suckless.org/dmenu/). Dmenu is a straightforward tool for creating simple menus. Simply pipe something into it, and it will display as a menu on the screen. It is used in this case to show the user read and select operations.

All of these script files interact as follows:

 1. [dbplnmpv.py](https://github.com/duartqx/dbplnmpv/blob/main/dbplmpv.py) is in charge of all database operations such as create, read, update, and delete.
 2. [dbmpv.py](https://github.com/duartqx/dbplnmpv/blob/main/dbmpv.py) is in charge of interacting with dbplnmpv.py via a simple, straightforward command-line interface.
 3. [dbanimeplaylist.sh](https://github.com/duartqx/dbplnmpv/blob/main/dbanimeplaylist.sh) is a bash script that runs dbmpv and outputs the results to dmenu. This is the main interface, which can be accessed via keybindings or a.desktop file on GNU/Linux. Before you can use it, you must change the three variables at the top: `DB_FILE`, `TABLE_NAME`, and `WATCH_FOLDER` to something you prefer. If `DB_FILE` or `TABLE_NAME` does not exist, `dbplnmpv.py` will create it for you.

 ## Usage

 1. **dmenu**/dbanimeplaylist.sh

	You can run dbanimeplaylist.sh if you have dmenu installed on your system, either from source or via your distro's package manager. Ddmenu will appear on the screen with four menu entries (Watch, Update, Watched, Add), and you can select any of them with the arrow keys on the keyboard and enter:

    <p align="center">
      <img src="https://github.com/duartqx/images/blob/main/dbanimeplaylistsh.png?raw=true" alt="dbanimeplaylist.sh" />
    </p>

	 1.1. Watch

		A secondary dmenu will show up listing the database entries (in this case anime episodes) that are marked as not watched, if you press enter in one of the rows the episode will be played in fullscreen using [mpv](https://mpv.io/). Behind the scenes this option also updates database rows to deleted=1 if their files have already been deleted.

	 1.2. Update

		A secondary dmenu will show up listing all rows that their file are still on disk, if you select one its watched status will flip

	 1.3. Watched

		Similar to Watch, but will list already watched entries and selecting it will also play their file with mpv.

	 1.4. Add

		It will add a row to the database with the contents of your clipboard as the title

 2. dbmpv

	dbanimeplaylist.sh is just a helper script that integrates dbmpv.py with dmenu and mpv; you can actually use dbmpv directly. When using it this way, you must always pass the positional arguments `DB FILE` and `TABLE NAME`.
For a comprehensive list of options, type and execute `dbmpv --help` on your terminal.

	### Examples:

	 - `--create`:

         This option will write a row

		   `dbmpv "$HOME/.local/share/playlists.db" animeplaylist --create "[ASW] Ars no Kyojuu - 10 [1080p HEVC][6C8C78F0].mkv"`

	 - 	`--read`:

         This will query for unwatched entries and print the results to standard output.

		   `dbmpv "$HOME/.local/share/playlists.db" animeplaylist --read`

		 - if you add the `-w/--watched` option you'll get watched entries instead.
		 - By default, the ordering is ascending; however, if you pass the `-d/--desc` option, the ordering will be inverted to descending.

	 - `--readall`:

         This option will output all rows, regardless of whether they are watched or not, but will ignore rows with deleted = 1.

		   `dbmpv "$HOME/.local/share/playlists.db" animeplaylist --read`

	 - `--update`:

		 Because the update option will update a row's watched status, you also needs to pass the `--id <id>` option.

		   `dbmpv "$HOME/.local/share/playlists.db" animeplaylist --update --id 234`
