from os import environ


MINDEBUG = environ.get('MINDEBUG', default=None)
if MINDEBUG is None:
    environ['MINDEBUG'] = '1'
    MINDEBUG = '1'

if MINDEBUG == '1':
    environ['REDIS_HOST'] = '127.0.0.1'

print('MINDEBUG', MINDEBUG)

if __name__ == "__main__":
    from anubis.app import create_app
    from anubis.models import db
    from flask_migrate import upgrade
    app = create_app()
    with app.app_context():
        if MINDEBUG == '1':
            db.create_all()
        else:
            upgrade()
    app.run('0.0.0.0', 5000, debug=True)
