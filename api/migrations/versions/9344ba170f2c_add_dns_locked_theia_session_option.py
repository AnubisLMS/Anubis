"""ADD dns-locked theia session option

Revision ID: 9344ba170f2c
Revises: c19902c1c91d
Create Date: 2022-12-24 15:09:52.096517

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "9344ba170f2c"
down_revision = "c19902c1c91d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("theia_session", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("network_dns_locked", sa.Boolean(), nullable=True)
        )

    conn = op.get_bind()
    with conn.begin():
        conn.execute("UPDATE `theia_session` SET `network_dns_locked` = 1 WHERE `network_policy` = 'os-student';")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("theia_session", schema=None) as batch_op:
        batch_op.drop_column("network_dns_locked")
    # ### end Alembic commands ###
