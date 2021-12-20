"""ADD late_exceptions

Revision ID: 716e3e14891d
Revises: a622f56b9050
Create Date: 2021-05-19 22:20:35.197173

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "716e3e14891d"
down_revision = "a622f56b9050"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "late_exception",
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("assignment_id", sa.String(length=128), nullable=False),
        sa.Column("due_date", sa.DateTime(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["assignment.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("user_id", "assignment_id"),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_general_ci',
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("late_exception")
    # ### end Alembic commands ###
