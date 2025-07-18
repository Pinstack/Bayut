"""add_agency_id_to_agents

Revision ID: 214fe5745f2e
Revises: 629a6ca77da7
Create Date: 2025-07-18 15:19:44.481884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '214fe5745f2e'
down_revision: Union[str, Sequence[str], None] = '629a6ca77da7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add agency_id column to agents table
    op.add_column('agents', sa.Column('agency_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'agents_agency_id_fkey',
        'agents', 'agencies',
        ['agency_id'], ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key constraint
    op.drop_constraint('agents_agency_id_fkey', 'agents', type_='foreignkey')
    
    # Drop agency_id column
    op.drop_column('agents', 'agency_id')
