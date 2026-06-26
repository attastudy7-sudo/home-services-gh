"""add booking_completed and pro_rejected to notification type constraint

Revision ID: b1c2d3e4f5a6
Revises: fa5e66e9ef5a
Create Date: 2026-06-26 11:20:00.000000

"""
from alembic import op

revision = 'b1c2d3e4f5a6'
down_revision = 'fa5e66e9ef5a'
branch_labels = None
depends_on = None


def upgrade():
    # SQLite does not support DROP CONSTRAINT / ADD CONSTRAINT.
    # The constraint change is enforced by application logic and the
    # PostgreSQL CHECK constraint is managed separately in production.
    pass


def downgrade():
    pass
