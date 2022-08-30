"""ADD email

Revision ID: 4f7efe8d8177
Revises: 70bf8c2bf6a4
Create Date: 2022-08-26 12:54:44.980069

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "4f7efe8d8177"
down_revision = "70bf8c2bf6a4"
branch_labels = None
depends_on = None

fix_lines = [
    "ALTER TABLE `anubis_config` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `assigned_student_question` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `assigned_student_response` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `assignment` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `assignment_question` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `assignment_repo` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `assignment_test` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `course` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `forum_category` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `forum_post` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `forum_post_comment` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `forum_post_in_category` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `forum_post_upvote` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `forum_post_viewed` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `in_course` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `late_exception` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `lecture_notes` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `professor_for_course` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `static_file` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `submission` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `submission_build` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `submission_test_result` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `ta_for_course` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `theia_image` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `theia_image_tag` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `theia_paste` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `theia_session` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
    "ALTER TABLE `user` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",

    "ALTER TABLE `anubis_config` MODIFY `value` varchar(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `assigned_student_question` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `assignment` MODIFY `course_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `assignment` MODIFY `unique_code` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `assignment` MODIFY `theia_image_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `assignment` MODIFY `theia_image_tag_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `assignment_question` MODIFY `assignment_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `assignment_repo` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `assignment_test` MODIFY `assignment_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `course` MODIFY `join_code` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `course` MODIFY `theia_default_image_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `course` MODIFY `github_ta_team_slug` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `forum_category` MODIFY `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `forum_category` MODIFY `course_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `forum_post` MODIFY `course_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `forum_post_comment` MODIFY `approved_by_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `forum_post_comment` MODIFY `parent_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `static_file` MODIFY `filename` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `static_file` MODIFY `path` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `static_file` MODIFY `content_type` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `submission` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `submission` MODIFY `token` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `submission_build` MODIFY `submission_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `submission_test_result` MODIFY `output_type` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `theia_image` MODIFY `title` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `theia_image` MODIFY `icon` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `theia_image` MODIFY `default_tag` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `theia_paste` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `theia_paste` MODIFY `theia_session_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `theia_session` MODIFY `assignment_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `theia_session` MODIFY `repo_url` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `theia_session` MODIFY `course_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `theia_session` MODIFY `network_policy` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `theia_session` MODIFY `image_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",
    "ALTER TABLE `theia_session` MODIFY `image_tag_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;",

    "ALTER TABLE `alembic_version` MODIFY `version_num` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `anubis_config` MODIFY `key` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assigned_student_question` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assigned_student_question` MODIFY `assignment_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assigned_student_question` MODIFY `question_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assigned_student_response` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assigned_student_response` MODIFY `assigned_question_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assignment` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assignment_question` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assignment_repo` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assignment_repo` MODIFY `assignment_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assignment_repo` MODIFY `repo_url` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assignment_repo` MODIFY `netid` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `assignment_test` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `course` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_category` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post_comment` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post_comment` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post_comment` MODIFY `post_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post_in_category` MODIFY `post_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post_in_category` MODIFY `category_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post_upvote` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post_upvote` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post_upvote` MODIFY `post_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post_viewed` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `forum_post_viewed` MODIFY `post_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `in_course` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `in_course` MODIFY `course_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `late_exception` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `late_exception` MODIFY `assignment_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `lecture_notes` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `lecture_notes` MODIFY `static_file_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `lecture_notes` MODIFY `course_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `professor_for_course` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `professor_for_course` MODIFY `course_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `static_file` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `static_file` MODIFY `course_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `submission` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `submission` MODIFY `assignment_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `submission` MODIFY `assignment_repo_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `submission` MODIFY `commit` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `submission_build` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `submission_test_result` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `submission_test_result` MODIFY `submission_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `submission_test_result` MODIFY `assignment_test_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `ta_for_course` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `ta_for_course` MODIFY `course_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `theia_image` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `theia_image` MODIFY `image` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `theia_image_tag` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `theia_image_tag` MODIFY `image_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `theia_image_tag` MODIFY `tag` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `theia_image_tag` MODIFY `title` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `theia_image_tag` MODIFY `description` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `theia_paste` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `theia_session` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `theia_session` MODIFY `owner_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `user` MODIFY `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;",
    "ALTER TABLE `user` MODIFY `netid` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;"
]


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    conn = op.get_bind()
    for line in fix_lines:
        conn.execute(line)

    op.create_table(
        "email_template",
        sa.Column(
            "key",
            mysql.VARCHAR(
                charset="utf8mb4", collation="utf8mb4_general_ci", length=128
            ),
            nullable=False,
        ),
        sa.Column(
            "subject",
            mysql.VARCHAR(
                charset="utf8mb4", collation="utf8mb4_general_ci", length=1024
            ),
            nullable=True,
        ),
        sa.Column(
            "body",
            mysql.VARCHAR(
                charset="utf8mb4", collation="utf8mb4_general_ci", length=4096
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("key"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_general_ci",
    )
    op.create_index(
        op.f("ix_email_template_key"), "email_template", ["key"], unique=False
    )
    op.create_table(
        "email_event",
        sa.Column(
            "id",
            mysql.VARCHAR(
                charset="utf8mb4", collation="utf8mb4_general_ci", length=36
            ),
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            mysql.VARCHAR(
                charset="utf8mb4", collation="utf8mb4_general_ci", length=36
            ),
            nullable=True,
        ),
        sa.Column(
            "template_id",
            mysql.VARCHAR(
                charset="utf8mb4", collation="utf8mb4_general_ci", length=128
            ),
            nullable=True,
        ),
        sa.Column(
            "reference_id",
            mysql.VARCHAR(
                charset="utf8mb4", collation="utf8mb4_general_ci", length=36
            ),
            nullable=True,
        ),
        sa.Column(
            "reference_type",
            mysql.VARCHAR(
                charset="utf8mb4", collation="utf8mb4_general_ci", length=128
            ),
            nullable=True,
        ),
        sa.Column(
            "subject",
            mysql.VARCHAR(
                charset="utf8mb4", collation="utf8mb4_general_ci", length=2048
            ),
            nullable=True,
        ),
        sa.Column(
            "body",
            mysql.VARCHAR(
                charset="utf8mb4", collation="utf8mb4_general_ci", length=8192
            ),
            nullable=True,
        ),
        sa.Column("created", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["email_template.key"],
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_general_ci",
    )
    op.create_index(
        op.f("ix_email_event_id"), "email_event", ["id"], unique=False
    )
    op.add_column(
        "user",
        sa.Column("deadline_email_enabled", sa.Boolean()),
    )
    op.add_column(
        "user",
        sa.Column("release_email_enabled", sa.Boolean()),
    )
    conn = op.get_bind()
    conn.execute('UPDATE `user` SET `deadline_email_enabled` = 1;')
    conn.execute('UPDATE `user` SET `release_email_enabled` = 1;')
    op.alter_column('user', 'deadline_email_enabled', type_=sa.Boolean(), nullable=False)
    op.alter_column('user', 'release_email_enabled', type_=sa.Boolean(), nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "release_email_enabled")
    op.drop_column("user", "deadline_email_enabled")
    op.drop_index(op.f("ix_email_event_id"), table_name="email_event")
    op.drop_table("email_event")
    op.drop_index(op.f("ix_email_template_key"), table_name="email_template")
    op.drop_table("email_template")
    # ### end Alembic commands ###
