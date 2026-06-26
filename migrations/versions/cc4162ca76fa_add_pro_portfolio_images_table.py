"""add pro_portfolio_images table

Revision ID: cc4162ca76fa
Revises: b1c2d3e4f5a6
Create Date: 2026-06-26 18:48:27.647573

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = 'cc4162ca76fa'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pro_portfolio_images',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('pro_id', UUID(), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('caption', sa.String(length=255), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['pro_id'], ['pro_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('pro_portfolio_images')
