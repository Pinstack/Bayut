"""add_unique_locations_and_property_locations_tables

Revision ID: 69eef7c710d7
Revises: cc17a6ddfc89
Create Date: 2025-07-18 11:22:45.417690

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69eef7c710d7'
down_revision: Union[str, Sequence[str], None] = 'cc17a6ddfc89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'unique_locations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('name_l1', sa.String(), nullable=True),
        sa.Column('slug', sa.String(), nullable=True),
        sa.Column('slug_l1', sa.String(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('unique_locations.id'), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.UniqueConstraint('external_id', 'level', name='uq_unique_locations_external_id_level')
    )
    op.create_table(
        'property_locations',
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('properties.id'), primary_key=True),
        sa.Column('location_id', sa.Integer(), sa.ForeignKey('unique_locations.id'), primary_key=True),
        sa.Column('hierarchy_level', sa.Integer(), primary_key=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('property_locations')
    op.drop_table('unique_locations')
