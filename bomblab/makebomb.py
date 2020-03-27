from os import system, makedirs, environ
from random import choice
import string

CFLAGS     = '-Wall -m32 -no-pie'
BOMBFLAGS  = '-DNOTIFY'
SERVERNAME = environ.get('DOMAIN')
SERVERPORT = '80'
NOTIFYFLAG = '-n'
LABID      = 'E_HW'


def get_phases():
    return '-p ' + ''.join(choice('abc') for _ in range(6))


def get_userpass():
    return ''.join(choice(string.ascii_letters) for _ in range(20))


def makebomb(bombnum, username, app):
    """
    This function takes a unique bombnum and a username, and generates all the bomblab files.
    There are 3 distinct stages for compiling a bomblab.

    - Generate the users unique bomblab along with a solution
    - Generate a copy of the bomblab that does not report to the grading server
    - Cleaup files

    The phases variable is where the randomization between students bomblabs comes into play.
    It will generate a string of 6 random abc's that represent the different versions of each
    phase that will be compiled.

    The entire src directory will be copied to a temp directory in /tmp where the all the compilation
    will happen. Once this is done, all output files will be copied to the bombs/ directory.

    This function will return True on success, False otherwise.
    """

    phases = get_phases() # this will return something like "-p abacac"
    userpass = get_userpass() # gernate random password for the api to verify reported events
    bombdir = 'DATA/bombs/bomb{}'.format(bombnum)
    makedirs(bombdir)

    if system(f'cp -r ./src /tmp/src{bombnum}; cd /tmp/src{bombnum}; make -s cleanall') != 0:
        print('error setting up src')
        return False

    if system(f'cd /tmp/src{bombnum}; export CFLAGS="{CFLAGS}" SERVERNAME="result.{SERVERNAME}" SERVERPORT="{SERVERPORT}" USERID="{username}" USERPWD="{userpass}" LABID="{LABID}" BOMBFLAGS="{BOMBFLAGS}" NOTIFYFLAG="{NOTIFYFLAG}" BOMBPHASES="{phases}" BOMBID="{bombnum}"; make -e bomb; make -e bomb-solve; make solution.txt') != 0:
        app.logger.debug(f'error making bomb | {bombnum} | {username}')
        return False

    if system(f'cd /tmp/src{bombnum}; rm -f *.o bomb-quite; export CFLAGS="{CFLAGS}"; export BOMBFLAGS="-DNONOTIFY"; export BOMBPHASES="{phases}"; export BOMBID="{bombnum}"; make -e bomb-quiet') != 0:
        app.logger.debug(f'error making bomb-quite | {bombnum} | {username}')
        return False

    if system(f'cp /tmp/src{bombnum}/bomb /tmp/src{bombnum}/bomb-quiet /tmp/src{bombnum}/bomb.c /tmp/src{bombnum}/phases.c /tmp/src{bombnum}/solution.txt {bombdir}') != 0:
        app.logger.debug(f'error copying files | {bombnum} | {username}')
        return False

    if system(f'rm -rf /tmp/src{bombnum}') != 0:
        app.logger.debug(f'error cleaning up source dir | {bombnum} | {username}')
        return False

    with open(bombdir + '/ID', 'w') as f:
        f.write(username + '\n')
        f.close()

    with open(bombdir + '/PASSWORD', 'w') as f:
        f.write(userpass + '\n')
        f.close()

    with open(bombdir + '/README', 'w') as f:
        f.write(
            f'This is bomb {bombnum}.\n'
            f'It belongs to {username}\n'
        )
        f.close()

    return True
