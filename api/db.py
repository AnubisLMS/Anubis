from anubis.models import db
from anubis import create_app

if __name__ == "__main__":
    create_app()
    db.create_all()
