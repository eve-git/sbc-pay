"""distribution_code_changes

Revision ID: 6f0fe9f23d8c
Revises: b6e28faea978
Create Date: 2021-01-27 14:07:28.400759

"""
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


today = datetime.today().strftime('%Y-%m-%d')

# revision identifiers, used by Alembic.
revision = '6f0fe9f23d8c'
down_revision = 'b6e28faea978'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    disbursement_status_codes = op.create_table('disbursement_status_codes',
                                                sa.Column('code', sa.String(length=20), nullable=False),
                                                sa.Column('description', sa.String(length=200), nullable=False),
                                                sa.PrimaryKeyConstraint('code')
                                                )
    op.bulk_insert(
        disbursement_status_codes,
        [
            {'code': 'UPLOADED', 'description': 'Uploaded disbursement report'},
            {'code': 'ACKNOWLEDGED', 'description': 'Received ack from disbursement'},
            {'code': 'ERRORED', 'description': 'Error in disbursement file'},
            {'code': 'COMPLETED', 'description': 'Completed disbursement'}
        ]
    )

    op.create_table('ejv_files',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('created_on', sa.DateTime(), nullable=False),
                    sa.Column('completed_on', sa.DateTime(), nullable=True),
                    sa.Column('is_distribution', sa.Boolean(), nullable=True),
                    sa.Column('file_ref', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_ejv_files_file_ref'), 'ejv_files', ['file_ref'], unique=False)
    op.create_table('ejv_invoice_links',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('invoice_id', sa.Integer(), nullable=False),
                    sa.Column('ejv_file_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['ejv_file_id'], ['ejv_files.id'], ),
                    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.drop_table('daily_payment_batch_links')
    op.drop_table('ejv_batch_links')
    op.drop_table('daily_payment_batches')
    op.drop_table('ejv_batches')

    op.alter_column('distribution_codes', 'memo_name', nullable=True, new_column_name='name')
    # op.add_column('distribution_codes', sa.Column('name', sa.String(length=50), nullable=True))
    op.add_column('distribution_codes', sa.Column('disbursement_distribution_code_id', sa.Integer(), nullable=True))
    op.add_column('distribution_codes', sa.Column('service_fee_distribution_code_id', sa.Integer(), nullable=True))
    op.create_foreign_key('service_fee_distribution_code_id_fk', 'distribution_codes', 'distribution_codes',
                          ['service_fee_distribution_code_id'], ['distribution_code_id'])
    op.create_foreign_key('disbursement_distribution_code_id_fk', 'distribution_codes', 'distribution_codes',
                          ['disbursement_distribution_code_id'], ['distribution_code_id'])

    # Query all distribution codes and create a new record for the service fees.

    conn = op.get_bind()

    res = conn.execute(
        sa.text(" select distinct service_fee_memo_name, service_fee_stob, service_fee_line, service_fee_client, service_fee_project_code, service_fee_responsibility_centre, distribution_code_id "
        " from distribution_codes where service_fee_memo_name is not null and service_fee_stob is not null;"))
    results = res.fetchall()
    for result in results:
        service_fee_memo_name = result[0]
        service_fee_stob = result[1]
        service_fee_line = result[2]
        service_fee_client = result[3]
        service_fee_project_code = result[4]
        service_fee_responsibility_centre = result[5]
        distribution_code_id = result[6]
        print('distribution_code_id..', distribution_code_id)

        # Check if there is a record existing with the service_fee_responsibility_centre as that's unique.
        res = conn.execute(sa.text(f"select distribution_code_id from distribution_codes "
                           f"where stob='{service_fee_stob}' and service_line='{service_fee_line}' and client='{service_fee_client}' "
                           f" and project_code='{service_fee_project_code}' and responsibility_centre='{service_fee_responsibility_centre}' "
                           f"and service_fee_distribution_code_id is null"))
        results = res.fetchall()
        service_fee_distribution_code_id = None if len(results) == 0 else results[0][0]
        print('service_fee_distribution_code_id --->', service_fee_distribution_code_id)
        if service_fee_distribution_code_id is None:
            op.execute(
                "insert into distribution_codes (created_on, name, client, responsibility_centre, service_line, stob, project_code, start_date, created_by)"
                f" values ('{datetime.now(tz=timezone.utc)}', '{service_fee_memo_name}', '{service_fee_client}', '{service_fee_responsibility_centre}', '{service_fee_line}',"
                f"'{service_fee_stob}', '{service_fee_project_code}', '{today}', 'alembic');")

            # Get the inserted record id
            res = conn.execute(sa.text(f"select distribution_code_id from distribution_codes "
                               f"where stob='{service_fee_stob}' and service_line='{service_fee_line}' and client='{service_fee_client}' "
                               f" and project_code='{service_fee_project_code}' and responsibility_centre='{service_fee_responsibility_centre}' "
                               f"and service_fee_distribution_code_id is null"))

            service_fee_distribution_code_id = res.fetchall()[0][0]

        print('service_fee_distribution_code_id ', service_fee_distribution_code_id)
        # update the main record with service_fee_distribution_code_id
        op.execute(
            f"update distribution_codes set service_fee_distribution_code_id='{service_fee_distribution_code_id}' where distribution_code_id={distribution_code_id}")

    op.execute("update distribution_codes set service_fee_distribution_code_id=null where name='NSF';")
    op.drop_column('distribution_codes', 'service_fee_stob')
    op.drop_column('distribution_codes', 'service_fee_memo_name')
    op.drop_column('distribution_codes', 'service_fee_line')
    op.drop_column('distribution_codes', 'service_fee_client')
    op.drop_column('distribution_codes', 'service_fee_project_code')
    op.drop_column('distribution_codes', 'service_fee_responsibility_centre')
    op.add_column('invoices', sa.Column('disbursement_status_code', sa.String(length=20), nullable=True))
    op.create_foreign_key('disbursement_status_codes_fk', 'invoices', 'disbursement_status_codes',
                          ['disbursement_status_code'], ['code'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('disbursement_status_codes_fk', 'invoices', type_='foreignkey')
    op.drop_column('invoices', 'disbursement_status_code')
    op.add_column('distribution_codes',
                  sa.Column('service_fee_responsibility_centre', sa.VARCHAR(length=50), autoincrement=False,
                            nullable=True))
    op.add_column('distribution_codes',
                  sa.Column('service_fee_project_code', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('distribution_codes',
                  sa.Column('service_fee_client', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('distribution_codes',
                  sa.Column('service_fee_line', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('distribution_codes',
                  sa.Column('service_fee_memo_name', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('distribution_codes',
                  sa.Column('service_fee_stob', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    # op.add_column('distribution_codes',
    #               sa.Column('memo_name', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.drop_constraint('service_fee_distribution_code_id_fk', 'distribution_codes', type_='foreignkey')
    op.drop_constraint('disbursement_distribution_code_id_fk', 'distribution_codes', type_='foreignkey')
    op.drop_column('distribution_codes', 'service_fee_distribution_code_id')
    # op.drop_column('distribution_codes', 'name')
    op.alter_column('distribution_codes', 'name', nullable=True, new_column_name='memo_name')
    op.drop_column('distribution_codes', 'disbursement_distribution_code_id')
    op.drop_table('ejv_invoice_links')
    op.drop_index(op.f('ix_ejv_files_file_ref'), table_name='ejv_files')
    op.drop_table('ejv_files')
    op.drop_table('disbursement_status_codes')
    # ### end Alembic commands ###
