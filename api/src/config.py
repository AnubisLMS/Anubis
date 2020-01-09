import os


class Config:
    SECRET_KEY=os.urandom(32)

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:password@{}/os'.format(
        os.environ.get('DB_HOST', 'db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    REPO_SKELETAL = 'https://github.com/os3224/helloworld-'

    def __init__(self):
        if os.environ.get('DEBUG', None):
            self.DEBUG = True
