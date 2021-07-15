"""ADD accepted column

Revision ID: a622f56b9050
Revises: bf3ae1de1d12
Create Date: 2021-05-19 20:33:45.552222

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "a622f56b9050"
down_revision = "bf3ae1de1d12"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("name", table_name="assignment")
    op.drop_index("pipeline_image", table_name="assignment")
    op.alter_column(
        "assignment_question",
        "pool",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    op.drop_index(
        "ix_assignment_question_sequence", table_name="assignment_question"
    )
    op.create_index(
        op.f("ix_assignment_question_pool"),
        "assignment_question",
        ["pool"],
        unique=False,
    )
    op.add_column(
        "submission", sa.Column("accepted", sa.Boolean(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("submission", "accepted")
    op.drop_index(
        op.f("ix_assignment_question_pool"), table_name="assignment_question"
    )
    op.create_index(
        "ix_assignment_question_sequence",
        "assignment_question",
        ["pool"],
        unique=False,
    )
    op.alter_column(
        "assignment_question",
        "pool",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=True,
    )
    op.create_index(
        "pipeline_image", "assignment", ["pipeline_image"], unique=False
    )
    op.create_index("name", "assignment", ["name"], unique=False)
    # ### end Alembic commands ###
