"""Create Investor table.

Revision ID: a4ec79c46905
Revises: 
Create Date: 2016-07-03 15:59:59.007108

"""

# revision identifiers, used by Alembic.
revision = 'a4ec79c46905'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
      'investors',
      sa.Column('id', sa.Integer, primary_key=True),
      sa.Column('first_name', sa.String, nullable=False),
      sa.Column('last_name', sa.String, nullable=False),
      sa.Column('email', sa.String, nullable=False, unique=True),
      sa.Column('password_digest', sa.String(50)),
      sa.Column('access_token', sa.String(50)),
      sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
      sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now()),
   )

def downgrade():
    op.drop_table('investors')
