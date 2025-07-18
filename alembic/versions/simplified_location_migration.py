"""Create simplified location tables

Revision ID: simplified_location_migration
Revises: 69eef7c710d7
Create Date: 2025-07-18 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'simplified_location_migration'
down_revision: Union[str, Sequence[str], None] = '69eef7c710d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create simplified location tables."""
    
    # Create simplified_locations table
    op.create_table(
        'simplified_locations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('name_ar', sa.String(), nullable=True),
        sa.Column('slug', sa.String(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False),  # 1=city, 2=district, 3=street
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('simplified_locations.id'), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.UniqueConstraint('name', 'level', name='uq_simplified_locations_name_level')
    )
    
    # Create simplified_properties table
    op.create_table(
        'simplified_properties',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('external_id', sa.String(), unique=True, nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('title_ar', sa.String(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),  # Human-readable location string
        sa.Column('location_id', sa.Integer(), sa.ForeignKey('simplified_locations.id'), nullable=True),
        sa.Column('area', sa.Float(), nullable=True),
        sa.Column('bedrooms', sa.Integer(), nullable=True),
        sa.Column('bathrooms', sa.Integer(), nullable=True),
        sa.Column('property_type', sa.String(), nullable=True),
        sa.Column('purpose', sa.String(), nullable=True),
        sa.Column('permit_number', sa.String(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('extra_fields', sa.JSON(), nullable=True),
        sa.Column('agency_id', sa.Integer(), sa.ForeignKey('agencies.id'), nullable=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id'), nullable=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=True)
    )
    
    # Update existing tables to reference simplified_properties
    op.create_table(
        'simplified_media',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('simplified_properties.id'), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True)
    )
    
    op.create_table(
        'simplified_payment_plans',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('simplified_properties.id'), nullable=False),
        sa.Column('plan_type', sa.String(), nullable=True),
        sa.Column('down_payment', sa.Float(), nullable=True),
        sa.Column('installments', sa.JSON(), nullable=True)
    )
    
    op.create_table(
        'simplified_documents',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('simplified_properties.id'), nullable=False),
        sa.Column('doc_type', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Remove simplified location tables."""
    op.drop_table('simplified_documents')
    op.drop_table('simplified_payment_plans')
    op.drop_table('simplified_media')
    op.drop_table('simplified_properties')
    op.drop_table('simplified_locations') 