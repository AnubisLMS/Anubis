import sys

if '' in sys.path:
    sys.path.remove('')

from anubis_autograde.cli import main

if __name__ == '__main__':
    main()
