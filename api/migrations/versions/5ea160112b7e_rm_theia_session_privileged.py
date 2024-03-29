"""RM theia session privileged

Revision ID: 5ea160112b7e
Revises: 2faa37dff9d0
Create Date: 2022-09-19 21:46:31.860537

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "5ea160112b7e"
down_revision = "2faa37dff9d0"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("theia_session", "privileged")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "theia_session",
        sa.Column(
            "privileged",
            mysql.TINYINT(display_width=1),
            autoincrement=False,
            nullable=True,
        ),
    )
    # ### end Alembic commands ###
