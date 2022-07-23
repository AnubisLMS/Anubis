"""CHG uuid primary keys

Revision ID: 8099d1e3fafb
Revises: bdc6f7395c95
Create Date: 2022-07-22 21:35:49.253267

"""
import uuid

from alembic import op

# revision identifiers, used by Alembic.
revision = "8099d1e3fafb"
down_revision = "bdc6f7395c95"
branch_labels = None
depends_on = None


def _uuid():
    return str(uuid.uuid4())


tables = ['anubis_config', 'user', 'course', 'ta_for_course', 'professor_for_course', 'in_course', 'assignment',
          'assignment_repo', 'assignment_test', 'assignment_question', 'assigned_student_question',
          'assigned_student_response', 'submission', 'submission_test_result', 'submission_build', 'theia_image',
          'theia_image_tag', 'theia_session', 'theia_paste', 'static_file', 'late_exception', 'lecture_notes',
          'forum_post', 'forum_category', 'forum_post_in_category', 'forum_post_viewed', 'forum_post_comment',
          'forum_post_upvote']


def migrate_ids(conn, table_name: str, key_name: str | list = None):
    print(f'Migrating table {table_name} to new uuid format')

    if key_name is None:
        key_name = table_name + '_id'
    if not isinstance(key_name, list):
        key_name: list[str] = [key_name]

    key_name: list[str]

    i = 0
    limit = 1000

    key_sub_tables = dict()
    for _key_name in key_name:
        key_sub_tables[_key_name] = set()
        for sub_table_name in tables:
            r1 = conn.execute(
                'select 1 from `information_schema`.`columns` where `TABLE_SCHEMA` = %s and `TABLE_NAME` = %s and `COLUMN_NAME` = %s',
                ('anubis', sub_table_name, _key_name)
            )
            key_exists = r1.fetchone() is not None
            if key_exists:
                key_sub_tables[_key_name].add(sub_table_name)

    while True:
        r = conn.execute(f'select id from `{table_name}` limit {limit} offset {i * limit};')
        items = r.fetchall()

        for item in items:
            if item is None:
                break

            old_id, = item
            new_id = _uuid()

            conn.execute(f'update `{table_name}` set `id` = %s where `id` = %s;',
                         (new_id, old_id))

            for _key_name, sub_tables in key_sub_tables.items():
                for _sub_table_name in sub_tables:
                    conn.execute(f'update `{_sub_table_name}` set `{_key_name}` = %s where `{_key_name}` = %s;',
                                 (new_id, old_id))

        if len(items) < limit:
            break

        del items  # help gc
        i += 1


def upgrade():
    conn = op.get_bind()

    with conn.begin() as trx:
        conn.execute('SET FOREIGN_KEY_CHECKS=0;')

        migrate_ids(conn, 'user', ['owner_id', 'approved_by_id'])
        migrate_ids(conn, 'course')
        migrate_ids(conn, 'assignment')
        migrate_ids(conn, 'assignment_repo')
        migrate_ids(conn, 'assignment_test')
        migrate_ids(conn, 'assignment_question')
        migrate_ids(conn, 'assigned_student_question')
        migrate_ids(conn, 'assigned_student_response')
        migrate_ids(conn, 'submission')
        migrate_ids(conn, 'submission_test_result')
        migrate_ids(conn, 'submission_build')
        migrate_ids(conn, 'theia_image', 'image_id')
        migrate_ids(conn, 'theia_image_tag', 'image_tag_id')
        migrate_ids(conn, 'theia_session')
        migrate_ids(conn, 'theia_paste')
        migrate_ids(conn, 'static_file')
        migrate_ids(conn, 'forum_post', 'post_id')
        migrate_ids(conn, 'forum_category', 'category_id')
        migrate_ids(conn, 'forum_post_comment', 'parent_id')
        migrate_ids(conn, 'forum_post_upvote')

        conn.execute('SET FOREIGN_KEY_CHECKS=1;')

        trx.commit()


def downgrade():
    pass
