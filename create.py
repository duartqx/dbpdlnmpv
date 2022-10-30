#!/usr/bin/env python
from dbpdlnmpv import DbPdlnMpv
from sys import argv, exit as _exit

if __name__ == '__main__':

    HELP = '''Missing argument!
        All of these are required:
            --db_file arg
            --table_name arg
            --title arg
            --watched arg
        '''

    if not argv[1:]:
        print(HELP)
        _exit(1)

    try:
        db_file = argv[ argv.index('--db_file') + 1 ]
        table_name = argv[ argv.index('--table_name') + 1 ]
        title = argv[ argv.index('--title') + 1 ]
        if argv.count('--watched'):
            watched = argv[ argv.index('--watched') + 1 ]
        else:
            watched = 0
    except IndexError:
        print(HELP)
        _exit(1)
    except ValueError as e:
        print(f'Missing {str(e).split()[0]} argument')
        _exit(1)

    ## Connects to database
    db = DbPdlnMpv(table_name, db_file)

    # Creates the entry
    db.create(title, watched)
    db.close()