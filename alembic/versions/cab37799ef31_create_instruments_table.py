"""Create instruments table.

Revision ID: cab37799ef31
Revises: a4ec79c46905
Create Date: 2016-07-03 16:20:33.482301

"""

# revision identifiers, used by Alembic.
revision = 'cab37799ef31'
down_revision = 'a4ec79c46905'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
  op.create_table(
    'instruments',
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String, nullable=False),
    sa.Column('symbol', sa.String, nullable=False),
    sa.Column('created_at', sa.DateTime, default=datetime.now),
    sa.Column('updated_at', sa.DateTime, default=datetime.now, onupdate=datetime.now),
  )


def downgrade():
  op.drop_table('instruments')
