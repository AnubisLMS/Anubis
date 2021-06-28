from flask_migrate import Migrate

migrate = Migrate()


@migrate.configure
def configure_alembic(config):
    config.config_file_name = 'alembic.ini'
    return config