import os

class Config:
    SECRET_KEY=os.urandom(32)

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:password@db/os'
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    def __init__(self):
        if os.environ.get('DEBUG', None):
            self.DEBUG = True
