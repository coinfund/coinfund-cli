"""Add issued_date to Shares

Revision ID: 3989f1a9b068
Revises: f1cb9f5d3e8a
Create Date: 2016-09-03 12:17:21.048047

"""

# revision identifiers, used by Alembic.
revision = '3989f1a9b068'
down_revision = 'f1cb9f5d3e8a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('shares', sa.Column('issued_date', sa.DateTime, nullable=False, server_default=sa.func.now()))

def downgrade():
    op.drop_column('shares', 'issued_date')
