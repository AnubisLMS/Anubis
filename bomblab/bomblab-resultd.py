#!/usr/bin/env python3

from flask import Flask, request
from flaskext.mysql import MySQL
from datetime import datetime
import logging
import ctypes
import utils

class Config:
    MYSQL_DATABASE_HOST='db'
    MYSQL_DATABASE_USER='root'
    MYSQL_DATABASE_PASSWORD='password'
    MYSQL_DATABASE_DB='bomblab'

app = Flask(__name__)
logging.basicConfig(filename='resultd.log', level=logging.DEBUG)

app.config.from_object(Config())

mysql = MySQL()
mysql.init_app(app)

@app.route('/')
@utils.log_event('bomblab', lambda: 'submission', lambda: True)
def index():
    """
    This function could not be more simple. We are just forwarding events that
    are reported into the database. We dont do any checking, or data enriching.
    As long as all the fields are defined, we just execute the query to insert
    the data.
    """

    userid = request.args.get('userid', None)
    userpwd = request.args.get('userpwd', None)
    labid = request.args.get('lab', None)
    result = request.args.get('result', None)

    """
    Since requests are forwarded from the traefik edge router, their packet's ip will be that of traefik.
    Traefik will put the original source IP in the X-Forwarded-For http header.
    """
    ip = utils.get_request_ip()

    """
    Verify that none of the fields are None
    """
    if any(i is None for i in [userid, userpwd, labid, result]):
        utils.esindex(
            'error',
            type='bomblab',
            logs='invalid request: {}'.format(
                '\n'.join([userid, userpwd, labid, result])
            ),
            netid=userid,
            submission=labid
        )
        return 'OK'

    """
    There is small chance that the bombnum will have been converted to a signed
    nagative value. If that is the case, we can correct for it easily.
    """
    try:
        result = result.split(':')
        bombid = int(result[0])
        if bombid <= 0:
            bombid = ctypes.c_uint(bombid).value
        result[0] = str(bombid)
        result = ':'.join(result)
    except:
        utils.esindex('error', type='bomblab', logs='int overflow', netid=userid, submission=labid)
        return 'OK'


    """
    This generates the current timestamp in the specific format that the bomblab-update.pl is expecting it to be.
    """
    date = datetime.utcnow().strftime('%c')

    """
    Get a connection to the database.
    """
    connection = mysql.get_db()

    """
    Log the event.
    """
    app.logger.debug(f'{ip} {date} {userid} {userpwd} {labid} {result}')

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO Submission (ip, `date`, userid, userpwd, labid, `result`) VALUES (%s, %s, %s, %s, %s, %s);',
                (ip, date, userid, userpwd, labid, result,),
            )
            connection.commit()
    finally:
        pass

    return 'OK'

if __name__ == '__main__':
    app.run('0.0.0.0', 80, debug=True)
