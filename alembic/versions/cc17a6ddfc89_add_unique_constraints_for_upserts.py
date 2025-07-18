"""add_unique_constraints_for_upserts

Revision ID: cc17a6ddfc89
Revises: fd80e6630fc4
Create Date: 2025-07-18 11:13:48.607590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc17a6ddfc89'
down_revision: Union[str, Sequence[str], None] = 'fd80e6630fc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add unique constraints for upsert operations
    op.create_unique_constraint('uq_agencies_name', 'agencies', ['name'])
    op.create_unique_constraint('uq_agents_name', 'agents', ['name'])
    op.create_unique_constraint('uq_projects_name', 'projects', ['name'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove unique constraints
    op.drop_constraint('uq_agencies_name', 'agencies', type_='unique')
    op.drop_constraint('uq_agents_name', 'agents', type_='unique')
    op.drop_constraint('uq_projects_name', 'projects', type_='unique')
