"""Add project table.

Revision ID: f46e4d1e9a08
Revises: 184e826cb0b2
Create Date: 2016-07-03 17:14:47.322130

"""

# revision identifiers, used by Alembic.
revision = 'f46e4d1e9a08'
down_revision = '184e826cb0b2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
  op.create_table('projects',
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(50), nullable=False),
    sa.Column('homepage', sa.String),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now()),
  )

def downgrade():
  op.drop_table('projects')
