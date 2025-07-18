"""
Migration Script: Complex → Simplified Location System

Run this script after applying the Alembic migration for simplified tables.
It will copy all data from the old location tables to the new simplified tables.
"""

from src.models import Property, UniqueLocation, PropertyLocation
from src.simplified_models import SimplifiedProperty, SimplifiedLocation
from src.db_utils import SessionLocal


def migrate_unique_locations(session):
    print("Migrating unique_locations → simplified_locations...")
    unique_locations = session.query(UniqueLocation).order_by(UniqueLocation.level).all()
    inserted = 0
    for ul in unique_locations:
        if ul.name is None:
            continue  # Skip locations with no name
        # Deduplicate by (name, level)
        exists = session.query(SimplifiedLocation).filter_by(name=ul.name, level=ul.level).first()
        if exists:
            continue
        # Only set parent_id if it exists in simplified_locations
        parent_id = ul.parent_id
        if parent_id:
            parent_exists = session.query(SimplifiedLocation).filter_by(id=parent_id).first()
            if not parent_exists:
                parent_id = None
        sl = SimplifiedLocation(
            external_id=ul.external_id,
            name=ul.name,
            name_ar=ul.name_l1,
            slug=ul.slug,
            level=ul.level,
            parent_id=parent_id,
            latitude=ul.latitude,
            longitude=ul.longitude
        )
        session.add(sl)
        inserted += 1
    session.commit()
    print(f"✅ Migrated {inserted} unique_locations (deduplicated by name, level, parents before children, skipped null names).")


def migrate_properties(session):
    print("Migrating properties → simplified_properties...")
    properties = session.query(Property).all()
    migrated = 0
    for prop in properties:
        # Find the most specific location for this property
        property_location = (
            session.query(PropertyLocation)
            .filter_by(property_id=prop.id)
            .order_by(PropertyLocation.hierarchy_level.desc())
            .first()
        )
        location_id = property_location.location_id if property_location else None
        # Only use location_id if it exists in simplified_locations
        if location_id:
            exists = session.query(SimplifiedLocation).filter_by(id=location_id).first()
            if not exists:
                location_id = None

        sp = SimplifiedProperty(
            external_id=prop.external_id,
            title=prop.title,
            title_ar=prop.title_ar,
            price=prop.price,
            currency=prop.currency,
            location=prop.location,
            location_id=location_id,
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
        session.add(sp)
        migrated += 1
    session.commit()
    print(f"✅ Migrated {migrated} properties.")


def main():
    session = SessionLocal()
    try:
        migrate_unique_locations(session)
        migrate_properties(session)
        print("\n🎉 Migration to simplified location system complete!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main() 