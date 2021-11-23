from os import environ

MIGRATE = environ.get('MIGRATE', default=None)
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

    app = create_app()
    if MINDEBUG == '1' and MIGRATE == '1':
        with app.app_context():
            db.create_all()
    app.run('0.0.0.0', 5000, debug=True)
