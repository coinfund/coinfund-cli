"""Create shares table.

Revision ID: 184e826cb0b2
Revises: cab37799ef31
Create Date: 2016-07-03 16:39:30.542459

"""

# revision identifiers, used by Alembic.
revision = '184e826cb0b2'
down_revision = 'cab37799ef31'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
  op.create_table('shares', 
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('date', sa.DateTime, server_default=sa.func.now()),
    sa.Column('investor_id', sa.Integer, sa.ForeignKey('investors.id')),
    sa.Column('units', sa.Integer, default=0, nullable=False),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now()),
  )

def downgrade():
  op.drop_table('shares')
