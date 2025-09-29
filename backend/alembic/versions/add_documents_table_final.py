"""add documents table final

Revision ID: add_documents_table_final
Revises: 45e1c8c538b3
Create Date: 2025-09-29 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_documents_table_final'
down_revision: Union[str, Sequence[str], None] = '45e1c8c538b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('file_path', sa.String(), nullable=False),
    sa.Column('file_type', sa.String(), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=False),
    sa.Column('uploaded_by', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_company_id'), 'documents', ['company_id'], unique=False)
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_uploaded_by'), 'documents', ['uploaded_by'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_documents_uploaded_by'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_company_id'), table_name='documents')
    op.drop_table('documents')
