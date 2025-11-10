"""Add procurement tables

Revision ID: 541bcdf11be4
Revises: e3c98d9fca8d
Create Date: 2025-11-10 11:48:49.808001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '541bcdf11be4'
down_revision: Union[str, Sequence[str], None] = 'e3c98d9fca8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enums using raw SQL to handle if exists
    op.execute("CREATE TYPE IF NOT EXISTS vendor_status AS ENUM ('active', 'inactive')")
    op.execute("CREATE TYPE IF NOT EXISTS purchase_order_status AS ENUM ('pending', 'approved', 'rejected', 'completed')")
    op.execute("CREATE TYPE IF NOT EXISTS inventory_status AS ENUM ('in_stock', 'low_stock', 'out_of_stock')")

    # Create vendors table
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact_email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('status', vendor_status, nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vendors_id'), 'vendors', ['id'], unique=False)

    # Create purchase_orders table
    op.create_table(
        'purchase_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('item_name', sa.String(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', po_status, nullable=False),
        sa.Column('approver_id', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('bids', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_orders_id'), 'purchase_orders', ['id'], unique=False)

    # Create inventory_items table
    op.create_table(
        'inventory_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('expiry_date', sa.DateTime(), nullable=True),
        sa.Column('status', inventory_status, nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_items_id'), 'inventory_items', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_inventory_items_id'), table_name='inventory_items')
    op.drop_table('inventory_items')
    op.drop_index(op.f('ix_purchase_orders_id'), table_name='purchase_orders')
    op.drop_table('purchase_orders')
    op.drop_index(op.f('ix_vendors_id'), table_name='vendors')
    op.drop_table('vendors')

    # Drop enums
    inventory_status = sa.Enum('in_stock', 'low_stock', 'out_of_stock', name='inventory_status')
    inventory_status.drop(op.get_bind())
    po_status = sa.Enum('pending', 'approved', 'rejected', 'completed', name='purchase_order_status')
    po_status.drop(op.get_bind())
    vendor_status = sa.Enum('active', 'inactive', name='vendor_status')
    vendor_status.drop(op.get_bind())
