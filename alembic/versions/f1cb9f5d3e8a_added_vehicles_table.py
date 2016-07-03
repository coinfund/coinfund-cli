"""Added vehicles table.

Revision ID: f1cb9f5d3e8a
Revises: f46e4d1e9a08
Create Date: 2016-07-03 17:33:33.533258

"""

# revision identifiers, used by Alembic.
revision = 'f1cb9f5d3e8a'
down_revision = 'f46e4d1e9a08'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
  op.create_table(
    'vehicles',
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(50), nullable=False),
    sa.Column('project_id', sa.Integer, sa.ForeignKey('projects.id')),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now()),
  )

def downgrade():
  op.drop_table('vehicles')