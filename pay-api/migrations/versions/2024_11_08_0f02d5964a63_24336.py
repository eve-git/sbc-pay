"""24336 - update short name history with missing column

Revision ID: 0f02d5964a63
Revises: b4362f3400b9
Create Date: 2024-11-08 13:53:51.269060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
# Note you may see foreign keys with distribution_codes_history
# For disbursement_distribution_code_id, service_fee_distribution_code_id
# Please ignore those lines and don't include in migration.

revision = '0f02d5964a63'
down_revision = 'b4362f3400b9'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('eft_short_names_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_generated', sa.Boolean(), nullable=False, server_default="0"))


def downgrade():
    with op.batch_alter_table('eft_short_names_history', schema=None) as batch_op:
        batch_op.drop_column('is_generated')
