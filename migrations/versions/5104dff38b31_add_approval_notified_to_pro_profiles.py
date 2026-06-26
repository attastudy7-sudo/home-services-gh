"""add approval_notified to pro_profiles

Revision ID: 5104dff38b31
Revises: cc4162ca76fa
Create Date: 2026-06-26 19:25:27.371076

"""
from alembic import op
import sqlalchemy as sa


revision = '5104dff38b31'
down_revision = 'cc4162ca76fa'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('pro_profiles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('approval_notified', sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table('pro_profiles', schema=None) as batch_op:
        batch_op.drop_column('approval_notified')
