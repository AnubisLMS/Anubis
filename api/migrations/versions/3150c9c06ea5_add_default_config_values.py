"""ADD default config values

Revision ID: 3150c9c06ea5
Revises: c87807debbda
Create Date: 2021-09-25 14:10:56.323603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3150c9c06ea5'
down_revision = 'c87807debbda'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    with conn.begin():
        conn.execute("delete from anubis_config;")
        conn.execute("insert into anubis_config (`key`, `value`) values "
                     "('AUTOGRADE_RECALCULATE_DAYS', '60'), "
                     "('THEIA_STALE_PROXY_MINUTES', '10'), "
                     "('THEIA_STALE_TIMEOUT_HOURS', '6'), "
                     "('THEIA_MAX_SESSIONS', '10'), "
                     "('PIPELINE_MAX_JOBS', '10');")


def downgrade():
    conn = op.get_bind()
    with conn.begin():
        conn.execute("delete from anubis_config;")
        conn.execute("insert into anubis_config (`key`, `value`) values "
                     "('MAX_IDES', '10'), "
                     "('MAX_JOBS', '10');")
