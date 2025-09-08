"""Make company_id nullable in users table

Revision ID: 0002
Revises: 0001
Create Date: 2025-08-30 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('users', 'company_id',
               existing_type=sa.Integer(),
               nullable=True)

def downgrade():
    op.alter_column('users', 'company_id',
               existing_type=sa.Integer(),
               nullable=False)
