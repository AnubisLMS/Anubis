import os

class Config:
    SECRET_KEY=os.urandom(32)

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:password@db/os'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    REPO_SKELETAL = 'https://github.com/os3224/helloworld-'

    def __init__(self):
        if os.environ.get('DEBUG', None):
            self.DEBUG = True
        if db_host := os.environ.get('DB_HOST', None):
            self.SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:password@{}/os'.format(
                db_host
            )
