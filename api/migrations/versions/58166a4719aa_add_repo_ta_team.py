"""ADD repo ta team

Revision ID: 58166a4719aa
Revises: 7bce3314f2d8
Create Date: 2022-01-15 20:29:16.361481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "58166a4719aa"
down_revision = "7bce3314f2d8"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "assignment_repo",
        sa.Column("ta_configured", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "course",
        sa.Column("github_ta_team_slug", sa.String(length=256), nullable=True),
    )
    conn = op.get_bind()
    with conn.begin():
        conn.execute('update assignment_repo set ta_configured = 1;')
        conn.execute('update course set github_ta_team_slug = \'tas\';')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("course", "github_ta_team_slug")
    op.drop_column("assignment_repo", "ta_configured")
    # ### end Alembic commands ###
