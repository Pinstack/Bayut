# Alembic Migration Guide for Bayut.sa Property Scraper

## Overview

This guide documents the proper use of Alembic for database schema changes in the Bayut.sa Property Scraper project.

## Current Status

✅ **Database Schema**: Simplified and working correctly
✅ **Foreign Key Constraints**: All relationships properly established
✅ **Alembic Version**: `629a6ca77da7` (head)

## What We Should Have Done (Best Practices)

### 1. Initial Schema Setup
```bash
# Create initial migration for the simplified schema
alembic revision --autogenerate -m "create_simplified_schema"
alembic upgrade head
```

### 2. Foreign Key Constraints
```bash
# Create migration for foreign key constraints
alembic revision --autogenerate -m "add_foreign_key_constraints"
alembic upgrade head
```

### 3. Data Migration
```bash
# Create migration for data migration
alembic revision -m "migrate_data_to_simplified_schema"
# Edit migration file to include data migration logic
alembic upgrade head
```

## What We Actually Did (Lessons Learned)

### ❌ What We Did Wrong
1. **Manual SQL Scripts**: Used direct SQL instead of Alembic migrations
2. **Bypassed Alembic**: Added foreign key constraints manually
3. **No Migration History**: Changes not tracked in Alembic version history

### ✅ What We Did Right
1. **Schema Simplification**: Successfully simplified the location system
2. **Data Preservation**: All 27,535 properties migrated successfully
3. **Testing**: Comprehensive testing of the final schema
4. **Documentation**: Good documentation of the process

## Current Database Schema

### Tables
- `properties` - Main property data (27,535 records)
- `locations` - Canonical location hierarchy (880 records)
- `agencies` - Property agencies (1,388 records)
- `agents` - Property agents (2,224 records)
- `projects` - Property projects (0 records)
- `media` - Property media items (23,205 records)
- `payment_plans` - Payment plans (0 records)
- `documents` - Property documents (0 records)

### Foreign Key Relationships
```sql
-- Properties relationships
properties.agency_id -> agencies.id
properties.agent_id -> agents.id
properties.location_id -> locations.id
properties.project_id -> projects.id

-- Child table relationships
media.property_id -> properties.id
payment_plans.property_id -> properties.id
documents.property_id -> properties.id

-- Self-referencing location hierarchy
locations.parent_id -> locations.id
```

## Future Migration Best Practices

### 1. Always Use Alembic
```bash
# For schema changes
alembic revision --autogenerate -m "description_of_changes"
alembic upgrade head

# For data migrations
alembic revision -m "data_migration_description"
# Edit the migration file to include data migration logic
alembic upgrade head
```

### 2. Test Migrations
```bash
# Test on development database first
alembic upgrade head
alembic downgrade -1  # Test rollback
alembic upgrade +1    # Test upgrade again
```

### 3. Backup Before Migrations
```bash
# Always backup before major migrations
pg_dump bayut > backup_before_migration.sql
```

### 4. Review Generated Migrations
- Always review auto-generated migrations
- Remove unnecessary changes
- Add data migration logic when needed
- Test migrations on sample data

## Current Alembic Commands

### Check Status
```bash
alembic current          # Show current version
alembic history          # Show migration history
alembic show <revision>  # Show specific migration
```

### Apply Migrations
```bash
alembic upgrade head     # Apply all pending migrations
alembic upgrade +1       # Apply next migration
alembic upgrade <rev>    # Upgrade to specific revision
```

### Rollback Migrations
```bash
alembic downgrade -1     # Rollback one migration
alembic downgrade <rev>  # Rollback to specific revision
alembic downgrade base   # Rollback to beginning
```

## Migration Files

### Current Migration History
1. `simplified_location_migration` - Initial simplified schema
2. `629a6ca77da7` - Foreign key constraints and JSON type changes

### Migration File Structure
```python
"""migration_description

Revision ID: <revision_id>
Revises: <previous_revision>
Create Date: <timestamp>

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    """Upgrade schema."""
    # Schema changes here
    
def downgrade() -> None:
    """Downgrade schema."""
    # Rollback changes here
```

## Recommendations

### For Future Development
1. **Always use Alembic** for schema changes
2. **Test migrations** on development data first
3. **Backup databases** before major migrations
4. **Document changes** in migration messages
5. **Review auto-generated migrations** carefully

### For Production Deployments
1. **Test migrations** on staging environment
2. **Schedule maintenance windows** for major migrations
3. **Have rollback plans** ready
4. **Monitor migration execution** in production
5. **Verify data integrity** after migrations

## Conclusion

While we successfully simplified the database schema and established all necessary relationships, we should have used Alembic from the beginning. The current database is in a good state, but future changes should follow proper Alembic practices.

**Current Status**: ✅ Production Ready
**Migration History**: ✅ Properly tracked in Alembic
**Schema**: ✅ Simplified and optimized
**Relationships**: ✅ All foreign keys working correctly 