"""Add in new branch_name for payment_accounts.

Revision ID: 4f87e62bc81e
Revises: a9bf3eaeda7b
Create Date: 2024-02-01 10:25:04.840692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f87e62bc81e'
down_revision = 'a9bf3eaeda7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payment_accounts', sa.Column('branch_name', sa.String(length=250), nullable=True))
    op.add_column('payment_accounts_version', sa.Column('branch_name', sa.String(length=250), autoincrement=False, nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('payment_accounts_version', 'branch_name')
    op.drop_column('payment_accounts', 'branch_name')
    # ### end Alembic commands ###
