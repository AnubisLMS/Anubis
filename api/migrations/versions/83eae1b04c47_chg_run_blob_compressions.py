"""CHG run blob compressions

Revision ID: 83eae1b04c47
Revises: 023ee1a8f6cd
Create Date: 2021-12-05 11:35:33.125548

"""
import gzip

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '83eae1b04c47'
down_revision = '023ee1a8f6cd'
branch_labels = None
depends_on = None


def process_compressed_column(conn, table, column, forward=True, batch_size=100):
    count = conn.execute('SELECT COUNT(id) FROM `{}`;'.format(table)).fetchone()[0]
    iterations = (count // batch_size) + 1
    for i in range(0, iterations):
        print('\r{:<12} :: {}/{}'.format(table, i + 1, iterations), end='', flush=True)
        rows = conn.execute(
            sa.sql.text('SELECT id, `{column}` FROM `{table}` LIMIT :batch_size OFFSET :offset;'.format(
                column=column if forward else '_' + column,
                table=table
            )),
            batch_size=batch_size,
            offset=i * batch_size,
        ).fetchall()

        if len(rows) == 0:
            break

        with conn.begin():
            for _id, _blob in rows:
                if _blob is None:
                    continue

                if isinstance(_blob, str):
                    _blob = _blob.encode()

                conn.execute(
                    sa.sql.text('UPDATE `{table}` SET `{column}` = :blob WHERE id = :id;'.format(
                        column='_' + column if forward else column, table=table
                    )),
                    blob=gzip.compress(_blob) if forward else gzip.decompress(_blob),
                    id=_id,
                )
            del rows
    print()


def upgrade():
    conn = op.get_bind()
    process_compressed_column(conn, 'static_file', 'blob', batch_size=1)
    process_compressed_column(conn, 'submission_build', 'stdout', batch_size=300)
    process_compressed_column(conn, 'submission_test_result', 'stdout', batch_size=300)


def downgrade():
    conn = op.get_bind()
    process_compressed_column(conn, 'static_file', 'blob', forward=False, batch_size=1)
    process_compressed_column(conn, 'submission_build', 'stdout', forward=False, batch_size=300)
    process_compressed_column(conn, 'submission_test_result', 'stdout', forward=False, batch_size=300)
