"""DEL uncompressed blobs

Revision ID: 58bdacf47c81
Revises: 83eae1b04c47
Create Date: 2021-12-05 11:36:53.083443

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "58bdacf47c81"
down_revision = "83eae1b04c47"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("static_file", "blob")
    # op.drop_column("submission_build", "stdout")
    # op.drop_column("submission_test_result", "stdout")


def downgrade():
    # op.add_column(
    #     "submission_test_result",
    #     sa.Column(
    #         "stdout", mysql.TEXT(collation="utf8mb4_unicode_ci"), nullable=True
    #     ),
    # )
    # op.add_column(
    #     "submission_build",
    #     sa.Column(
    #         "stdout", mysql.TEXT(collation="utf8mb4_unicode_ci"), nullable=True
    #     ),
    # )
    op.add_column("static_file", sa.Column("blob", mysql.LONGBLOB(), nullable=True))
