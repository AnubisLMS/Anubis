#!/usr/bin/env python3

from flask import Flask, Response, request, render_template, send_from_directory, send_file
from datetime import datetime
from makebomb import makebomb
from random import randint
from os.path import isdir
from os import system
import logging
import string
import json
import re
import utils

USERNAME_CHARSET = string.ascii_letters + string.digits


app = Flask(__name__)
utils.add_global_error_handler(app)

"""
This will forward all the lovely flask logging to the requestd.log file.
That file will be mounted back to ./log/requestd.log
"""
logging.basicConfig(filename='requestd.log', level=logging.DEBUG)

"""
Someone figured out that we weren't checking netids, so we added a check
to make sure people are putting in valid netids.
"""
netids = json.load(open('./netids.json'))


def validate(netid):
    return netid in netids

def gen_bomb_num():
    """
    Very low chance of race condition
    which is good enough for me
    """
    bombnum = randint(0, 0xffffff)
    return bombnum if not isdir('bombs/bomb{num}'.format(num=bombnum)) else gen_bomb_num()


@app.route('/', methods=['GET', 'POST'])
@utils.log_event('bomblab', lambda: 'new lab requested', lambda: request.method == 'POST')
def index():
    if request.method == 'POST':
        """
        A post request means the form was submitted and we need to validate the input,
        then generate a bomblab.
        """
        app.logger.debug('{} | {} bomblab request'.format(
            str(datetime.now()),
            utils.get_request_ip()
        ))

        """
        To prevent command injection, we must force a small set of valid characters users can use.
        """
        username = request.form.get('username', default=None)
        if username is None or not all(i in USERNAME_CHARSET for i in username):
            return 'Illegal character in username {username}'.format(
                username=username,
            )

        username = username.strip()

        """
        Here we validate that the username was in the netids.json file.
        """
        if not validate(username):
            return 'You must enter your netid'

        """
        This will return a random number for a bombid
        that has not been generated yet.
        """
        bombnum = gen_bomb_num()


        """
        This function will generate a new bomblab, and save its contents to the bombs directory.
        We definitely want to crash at this point if the bomblab was not properly generated.

        The function returns True if the generation was successful, False otherwise.
        """
        assert makebomb(bombnum, username, app)

        """
        We can now take the generated files, and archive the files we want to give to our
        users in a tarball file.
        """
        assert system(
            f'cd bombs; tar cf - bomb{bombnum}/README bomb{bombnum}/bomb.c bomb{bombnum}/bomb > bomb{bombnum}.tar'
        ) == 0

        """
        Since this is a tarball we are returning and not a plaintext html file we need to set some
        extra headers to let the users browser know they need to handle it differently.
        """
        with open(f'bombs/bomb{bombnum}.tar', 'rb') as f:
            resp = Response(f.read())
            resp.headers['Content-Type'] = 'application/x-tar'
            resp.headers['Content-Disposition'] = f'file; filename=bomb{bombnum}.tar'
            resp.headers['MIME-Version'] = '1.0'
            f.close()

        """
        Clean up the tarball, as we don't need it anymore
        """
        system(f'rm bombs/bomb{bombnum}.tar')

        """
        Log the successful event
        """
        app.logger.debug('{} | {} bomblab generated'.format(
            str(datetime.now()),
            utils.get_request_ip()
        ))

        utils.esindex('bomblab-gen', netid=username, bombid=bombnum)

        return resp
    return render_template('form.html')


@app.route('/scoreboard')
@utils.log_event('bomblab', lambda: 'scoreboard requested', lambda: True)
def scoreboard():
    return send_file('scoreboard.html')


if __name__ == '__main__':
    app.run(
        '0.0.0.0',
        5000,
        debug=True,
    )
