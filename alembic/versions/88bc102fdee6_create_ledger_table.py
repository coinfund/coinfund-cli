"""Create ledger table

Revision ID: 88bc102fdee6
Revises: 3989f1a9b068
Create Date: 2016-09-03 13:55:00.998754

"""

# revision identifiers, used by Alembic.
revision = '88bc102fdee6'
down_revision = '3989f1a9b068'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

kind_enum_values    = ('Contribution', 'Expense', 'Trade', 'Income', 'Reimbursement', 'Interest', 'Distribution', 'Gift')
kind_enum           = ENUM(*kind_enum_values, name='kind', create_type=False)

def upgrade():
  # enums
 
  op.create_table('ledger', 
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('date', sa.DateTime, server_default=sa.func.now()),
    sa.Column('kind', kind_enum, nullable=False),
    sa.Column('subkind', sa.String(50)),
    sa.Column('usd_value', sa.Numeric, nullable=False),
    sa.Column('qty_in', sa.Numeric),
    sa.Column('instr_in_id', sa.Integer, sa.ForeignKey('instruments.id')),
    sa.Column('qty_out', sa.Numeric),
    sa.Column('instr_out_id', sa.Integer, sa.ForeignKey('instruments.id')),
    sa.Column('contributor_id', sa.Integer, sa.ForeignKey('investors.id')),
    sa.Column('venue', sa.String(50)),
    sa.Column('vendor', sa.String(50)),
    sa.Column('tx_info', sa.String(256)),
    sa.Column('notes', sa.String(1024)),
    sa.Column('settled', sa.Boolean, nullable=False, default=True),
    sa.Column('source', sa.String(64)),
    sa.Column('vehicle_id', sa.Integer, sa.ForeignKey('vehicles.id')),
    sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now())
  )

def downgrade():
  op.drop_table('ledger')
