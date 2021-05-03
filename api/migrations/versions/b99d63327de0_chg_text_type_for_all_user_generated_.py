"""CHG text type for all user generated strings

Revision ID: b99d63327de0
Revises: 4331be83342a
Create Date: 2021-04-27 14:20:44.854766

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b99d63327de0'
down_revision = '4331be83342a'
branch_labels = None
depends_on = None


def upgrade():
    # User
    op.alter_column('user', 'github_username', type_=sa.TEXT(length=2 ** 16))
    op.alter_column('user', 'name', type_=sa.TEXT(length=2 ** 16))

    # Course
    op.alter_column('course', 'name', type_=sa.TEXT(length=2 ** 16))
    op.alter_column('course', 'course_code', type_=sa.TEXT(length=2 ** 16))
    op.alter_column('course', 'semester', type_=sa.TEXT(length=2 ** 16))
    op.alter_column('course', 'section', type_=sa.TEXT(length=2 ** 16))
    op.alter_column('course', 'professor', type_=sa.TEXT(length=2 ** 16))

    # Assignment
    op.alter_column('assignment', 'name', type_=sa.TEXT(length=2 ** 16))
    op.alter_column('assignment', 'description', type_=sa.TEXT(length=2 ** 16))
    op.alter_column('assignment', 'github_classroom_url', type_=sa.TEXT(length=2 ** 16))
    op.alter_column('assignment', 'pipeline_image', type_=sa.TEXT(length=2 ** 16))

    # Assignment repo
    op.alter_column('assignment_repo', 'github_username', type_=sa.TEXT(length=2 ** 16))
    op.alter_column('assignment_repo', 'repo_url', type_=sa.TEXT(length=2 ** 16))

    # Assignment test
    op.alter_column('assignment_test', 'name', type_=sa.TEXT(length=2 ** 16))
    op.alter_column('assignment_question', 'code_language', type_=sa.TEXT(length=2 ** 16))

    # Submission
    op.alter_column('submission', 'state', type_=sa.TEXT(length=2 ** 16))

    # Theia session
    op.alter_column('theia_session', 'state', type_=sa.TEXT(length=2 ** 16))
    op.alter_column('theia_session', 'cluster_address', type_=sa.TEXT(length=2 ** 16))


def downgrade():
    # User
    op.alter_column('user', 'github_username', type_=sa.String(256))
    op.alter_column('user', 'name', type_=sa.String(256))

    # Course
    op.alter_column('course', 'name', type_=sa.String(256))
    op.alter_column('course', 'course_code', type_=sa.String(256))
    op.alter_column('course', 'semester', type_=sa.String(256))
    op.alter_column('course', 'section', type_=sa.String(256))
    op.alter_column('course', 'professor', type_=sa.String(256))

    # Assignment
    op.alter_column('assignment', 'name', type_=sa.String(256))
    op.alter_column('assignment', 'description', type_=sa.String(256))
    op.alter_column('assignment', 'github_classroom_url', type_=sa.String(256))
    op.alter_column('assignment', 'pipeline_image', type_=sa.String(256))

    # Assignment repo
    op.alter_column('assignment_repo', 'github_username', type_=sa.String(256))
    op.alter_column('assignment_repo', 'repo_url', type_=sa.String(256))

    # Assignment test
    op.alter_column('assignment_test', 'name', type_=sa.String(256))
    op.alter_column('assignment_question', 'code_language', type_=sa.String(256))

    # Submission
    op.alter_column('submission', 'state', type_=sa.String(256))

    # Theia session
    op.alter_column('theia_session', 'state', type_=sa.String(256))
    op.alter_column('theia_session', 'cluster_address', type_=sa.String(256))
