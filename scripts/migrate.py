import pymysql
from datetime import datetime, timedelta
from pytz import timezone

eastern = timezone('US/Eastern')



con = pymysql.connect(
    'localhost',
    'root',
    'password',
    'os'
)

with con:
    cur = con.cursor()

    cur.execute('delete from assignments;')
    cur.execute(
        'insert into assignments (id, name, due_date, grace_date) values (1, %s, %s, %s);',
        (
            'os3224-assignment-1',
            eastern.localize(datetime(2020, 3, 7, 23, 55, 0)),
            eastern.localize(datetime(2020, 3, 8, 23, 55, 0))
        )
    )
    cur.execute(
        'insert into assignments (id, name, due_date, grace_date) values (2, %s, %s, %s);',
        (
            'os3224-assignment-2',
            eastern.localize(datetime(2020, 3, 7, 23, 55, 0)),
            eastern.localize(datetime(2020, 3, 8, 23, 55, 0))
        )
    )
    con.commit()
    cur.execute("SELECT id, assignment from submissions")
    submissions = cur.fetchall()

    cur.execute('ALTER TABLE submissions DROP COLUMN assignment;')
    cur.execute('alter table submissions add column assignmentid int')
    cur.execute('ALTER TABLE submissions ADD FOREIGN KEY (`assignmentid` ) REFERENCES `assignments` (`id` );')
    con.commit()

    for s in submissions:
        id, a = s
        cur.execute(
            'update submissions set assignmentid = %s where id = %s;',
            (1 if a == 'os3224-assignment-1' else 2, id)
        )


    con.commit()
    print(submissions)
