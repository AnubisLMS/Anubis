"""chg_rename_professor_to_professor_for_course

Revision ID: 49d73a536492
Revises: 65be3bf01dae
Create Date: 2021-07-18 12:57:52.105841

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "49d73a536492"
down_revision = "65be3bf01dae"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("course", "professor", new_column_name="professor_display_name", type_=sa.TEXT())


def downgrade():
    op.alter_column("course", "professor_display_name", new_column_name="professor", type_=sa.TEXT())
