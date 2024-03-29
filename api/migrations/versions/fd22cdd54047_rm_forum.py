"""RM forum

Revision ID: fd22cdd54047
Revises: f24845d5da2e
Create Date: 2023-01-16 21:47:16.976496

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "fd22cdd54047"
down_revision = "f24845d5da2e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("forum_post_comment", schema=None) as batch_op:
        batch_op.drop_index("ix_forum_post_comment_id")
    with op.batch_alter_table("forum_category", schema=None) as batch_op:
        batch_op.drop_index("ix_forum_category_id")
    with op.batch_alter_table("forum_post", schema=None) as batch_op:
        batch_op.drop_index("ix_forum_post_id")
    with op.batch_alter_table("forum_post_upvote", schema=None) as batch_op:
        batch_op.drop_index("ix_forum_post_upvote_id")

    for _ in range(5):
        for table_name in [
            "forum_post_comment",
            "forum_post_in_category",
            "forum_category",
            "forum_post_viewed",
            "forum_post_upvote",
            "forum_post"
        ]:
            try:
                op.drop_table(table_name)
            except:
                pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "forum_post_upvote",
        sa.Column("id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("owner_id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("post_id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("created", mysql.DATETIME(), nullable=True),
        sa.Column("last_updated", mysql.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["user.id"], name="forum_post_upvote_ibfk_1"
        ),
        sa.ForeignKeyConstraint(
            ["post_id"], ["forum_post.id"], name="forum_post_upvote_ibfk_2"
        ),
        sa.PrimaryKeyConstraint("id", "owner_id", "post_id"),
        mysql_collate="utf8mb4_general_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    with op.batch_alter_table("forum_post_upvote", schema=None) as batch_op:
        batch_op.create_index("ix_forum_post_upvote_id", ["id"], unique=False)

    op.create_table(
        "forum_post_viewed",
        sa.Column("owner_id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("post_id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("created", mysql.DATETIME(), nullable=True),
        sa.Column("last_updated", mysql.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["user.id"], name="forum_post_viewed_ibfk_1"
        ),
        sa.ForeignKeyConstraint(
            ["post_id"], ["forum_post.id"], name="forum_post_viewed_ibfk_2"
        ),
        sa.PrimaryKeyConstraint("owner_id", "post_id"),
        mysql_collate="utf8mb4_general_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_table(
        "forum_post",
        sa.Column("id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("owner_id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("course_id", mysql.VARCHAR(length=36), nullable=True),
        sa.Column(
            "visible_to_students",
            mysql.TINYINT(display_width=1),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "pinned",
            mysql.TINYINT(display_width=1),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "anonymous",
            mysql.TINYINT(display_width=1),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "seen_count",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("title", mysql.TEXT(), nullable=True),
        sa.Column("content", mysql.MEDIUMTEXT(), nullable=True),
        sa.Column("created", mysql.DATETIME(), nullable=True),
        sa.Column("last_updated", mysql.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(
            ["course_id"], ["course.id"], name="forum_post_ibfk_1"
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["user.id"], name="forum_post_ibfk_2"
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_general_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    with op.batch_alter_table("forum_post", schema=None) as batch_op:
        batch_op.create_index("ix_forum_post_id", ["id"], unique=False)

    op.create_table(
        "forum_category",
        sa.Column("id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("name", mysql.VARCHAR(length=128), nullable=True),
        sa.Column("course_id", mysql.VARCHAR(length=36), nullable=True),
        sa.Column("created", mysql.DATETIME(), nullable=True),
        sa.Column("last_updated", mysql.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(
            ["course_id"], ["course.id"], name="forum_category_ibfk_1"
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_general_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    with op.batch_alter_table("forum_category", schema=None) as batch_op:
        batch_op.create_index("ix_forum_category_id", ["id"], unique=False)

    op.create_table(
        "forum_post_in_category",
        sa.Column("post_id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("category_id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("created", mysql.DATETIME(), nullable=True),
        sa.Column("last_updated", mysql.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["forum_category.id"],
            name="forum_post_in_category_ibfk_1",
        ),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["forum_post.id"],
            name="forum_post_in_category_ibfk_2",
        ),
        sa.PrimaryKeyConstraint("post_id", "category_id"),
        mysql_collate="utf8mb4_general_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_table(
        "forum_post_comment",
        sa.Column("id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("owner_id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("post_id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("approved_by_id", mysql.VARCHAR(length=36), nullable=True),
        sa.Column(
            "anonymous",
            mysql.TINYINT(display_width=1),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "thread_start",
            mysql.TINYINT(display_width=1),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("content", mysql.TEXT(), nullable=True),
        sa.Column("created", mysql.DATETIME(), nullable=True),
        sa.Column("last_updated", mysql.DATETIME(), nullable=True),
        sa.Column("parent_id", mysql.VARCHAR(length=36), nullable=True),
        sa.ForeignKeyConstraint(
            ["approved_by_id"], ["user.id"], name="forum_post_comment_ibfk_1"
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["user.id"], name="forum_post_comment_ibfk_2"
        ),
        sa.ForeignKeyConstraint(
            ["post_id"], ["forum_post.id"], name="forum_post_comment_ibfk_3"
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_general_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    with op.batch_alter_table("forum_post_comment", schema=None) as batch_op:
        batch_op.create_index("ix_forum_post_comment_id", ["id"], unique=False)

    # ### end Alembic commands ###
