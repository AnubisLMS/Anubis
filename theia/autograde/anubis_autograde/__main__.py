import sys
import os

if '' in sys.path:
    sys.path.remove('')

if os.getcwd() == '/':
    os.chdir(os.environ.get('HOME', '/home/anubis'))

from anubis_autograde.cli import main

if __name__ == '__main__':
    main()
