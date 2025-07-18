# Migration Guide: Complex to Simplified Location System

## Overview

This guide helps you migrate from the complex 4-table location system to a simplified 2-table approach.

## Current vs Simplified System

### Current Complex System (4 Tables)
- `properties.location` - Simple string
- `locations` - Property-specific location details
- `unique_locations` - Canonical location master data
- `property_locations` - Junction table

### Simplified System (2 Tables)
- `simplified_properties.location` - Human-readable location string
- `simplified_locations` - Canonical location data with hierarchy

## Migration Steps

### Step 1: Create New Tables

Run the migration to create simplified tables:

```bash
# Create simplified tables alongside existing ones
alembic upgrade head
```

### Step 2: Migrate Data

```python
# Example migration script
from src.models import Property, Location, UniqueLocation, PropertyLocation
from src.simplified_models import SimplifiedProperty, SimplifiedLocation

def migrate_location_data():
    """Migrate data from complex to simplified system."""
    
    # 1. Migrate unique_locations to simplified_locations
    unique_locations = session.query(UniqueLocation).all()
    for ul in unique_locations:
        simplified_location = SimplifiedLocation(
            external_id=ul.external_id,
            name=ul.name,
            name_ar=ul.name_ar,
            slug=ul.slug,
            level=ul.level,
            parent_id=ul.parent_id,
            latitude=ul.latitude,
            longitude=ul.longitude
        )
        session.add(simplified_location)
    
    # 2. Migrate properties with location mapping
    properties = session.query(Property).all()
    for prop in properties:
        # Find the most specific location for this property
        property_location = session.query(PropertyLocation).filter_by(
            property_id=prop.id
        ).order_by(PropertyLocation.hierarchy_level.desc()).first()
        
        location_id = None
        if property_location:
            location_id = property_location.location_id
        
        # Create simplified property
        simplified_property = SimplifiedProperty(
            external_id=prop.external_id,
            title=prop.title,
            title_ar=prop.title_ar,
            price=prop.price,
            currency=prop.currency,
            location=prop.location,  # Keep the simple string
            location_id=location_id,  # Link to simplified location
            area=prop.area,
            bedrooms=prop.bedrooms,
            bathrooms=prop.bathrooms,
            property_type=prop.property_type,
            purpose=prop.purpose,
            permit_number=prop.permit_number,
            is_verified=prop.is_verified,
            extra_fields=prop.extra_fields,
            agency_id=prop.agency_id,
            agent_id=prop.agent_id,
            project_id=prop.project_id
        )
        session.add(simplified_property)
    
    session.commit()
```

### Step 3: Update Scraper

Update the scraper to use simplified location handling:

```python
# In bayut_scraper.py, replace complex location parsing with:

def parse_simplified_location(self, location_hierarchy):
    """Parse location hierarchy to simplified format."""
    if not location_hierarchy:
        return None, ""
    
    # Create human-readable location string
    location_parts = [loc.get('name', '') for loc in location_hierarchy if loc.get('name')]
    location_string = ", ".join(location_parts)
    
    # Find or create simplified location
    location_id = self.get_or_create_simplified_location(location_hierarchy)
    
    return location_id, location_string
```

### Step 4: Update Queries

Replace complex queries with simplified ones:

#### Before (Complex)
```sql
SELECT p.*, ul.name as location_name, ul.latitude, ul.longitude
FROM properties p
JOIN property_locations pl ON p.id = pl.property_id
JOIN unique_locations ul ON pl.location_id = ul.id
WHERE ul.name = 'Al Olaya' AND ul.level = 2;
```

#### After (Simplified)
```sql
SELECT p.*, l.name as location_name, l.latitude, l.longitude
FROM simplified_properties p
LEFT JOIN simplified_locations l ON p.location_id = l.id
WHERE p.location ILIKE '%Al Olaya%';
```

### Step 5: Test and Validate

```python
def validate_migration():
    """Validate that migration was successful."""
    
    # Check counts
    old_count = session.query(Property).count()
    new_count = session.query(SimplifiedProperty).count()
    
    print(f"Old properties: {old_count}")
    print(f"New properties: {new_count}")
    
    # Check location data
    old_locations = session.query(Location).count()
    new_locations = session.query(SimplifiedLocation).count()
    
    print(f"Old locations: {old_locations}")
    print(f"New locations: {new_locations}")
    
    # Test queries
    properties_in_olaya = session.query(SimplifiedProperty).filter(
        SimplifiedProperty.location.ilike('%Al Olaya%')
    ).count()
    
    print(f"Properties in Al Olaya: {properties_in_olaya}")
```

### Step 6: Remove Old Tables (Optional)

After validation, you can remove the old tables:

```sql
-- Drop old tables (be careful!)
DROP TABLE property_locations;
DROP TABLE locations;
DROP TABLE unique_locations;
DROP TABLE properties;

-- Rename new tables
ALTER TABLE simplified_properties RENAME TO properties;
ALTER TABLE simplified_locations RENAME TO locations;
```

## Benefits After Migration

### Performance Improvements
- **50% fewer table joins** for location queries
- **Faster queries** due to simpler schema
- **Reduced complexity** in application code

### Maintenance Benefits
- **Easier to understand** database schema
- **Simpler migrations** for future changes
- **Less code** to maintain

### Query Examples

#### Simple Location Search
```sql
-- Find properties in Al Olaya
SELECT * FROM simplified_properties 
WHERE location ILIKE '%Al Olaya%';
```

#### Location with Coordinates
```sql
-- Find properties with coordinates
SELECT p.*, l.latitude, l.longitude
FROM simplified_properties p
JOIN simplified_locations l ON p.location_id = l.id
WHERE l.latitude IS NOT NULL;
```

#### Location Aggregation
```sql
-- Count properties by location
SELECT location, COUNT(*) as count
FROM simplified_properties
GROUP BY location
ORDER BY count DESC;
```

## Rollback Plan

If you need to rollback:

1. **Keep old tables** during migration
2. **Test thoroughly** before removing old tables
3. **Have backup** of original data
4. **Gradual rollout** - migrate in batches

## Conclusion

The simplified location system provides:
- ✅ **Better performance**
- ✅ **Easier maintenance**
- ✅ **Simpler queries**
- ✅ **Same functionality**

The migration is straightforward and can be done with minimal downtime. 