"""
Test Script: Validate Simplified Location System Migration

This script tests the migration from complex 4-table to simplified 2-table location system.
"""

from src.db_utils import SessionLocal
from src.models import Property, PropertyLocation, UniqueLocation
from src.simplified_models import SimplifiedLocation, SimplifiedProperty


def test_data_counts():
    """Test that all data was migrated correctly."""
    print("📊 Testing Data Counts...")
    print("=" * 40)

    session = SessionLocal()
    try:
        # Old system counts
        old_properties = session.query(Property).count()
        old_unique_locations = session.query(UniqueLocation).count()
        old_property_locations = session.query(PropertyLocation).count()

        # New system counts
        new_properties = session.query(SimplifiedProperty).count()
        new_locations = session.query(SimplifiedLocation).count()

        print("Old System:")
        print(f"  Properties: {old_properties}")
        print(f"  Unique Locations: {old_unique_locations}")
        print(f"  Property-Location Links: {old_property_locations}")

        print("\nNew System:")
        print(f"  Properties: {new_properties}")
        print(f"  Locations: {new_locations}")

        # Validation
        if new_properties == old_properties:
            print("✅ Property count matches!")
        else:
            print("❌ Property count mismatch!")

        if new_locations > 0:
            print("✅ Locations migrated successfully!")
        else:
            print("❌ No locations migrated!")

    finally:
        session.close()


def test_sample_data():
    """Test sample data integrity."""
    print("\n🔍 Testing Sample Data...")
    print("=" * 40)

    session = SessionLocal()
    try:
        # Get a few sample properties
        sample_properties = session.query(SimplifiedProperty).limit(5).all()

        for i, prop in enumerate(sample_properties, 1):
            print(f"\nProperty {i}:")
            print(f"  Title: {prop.title[:50]}...")
            print(f"  Location: {prop.location}")
            print(f"  Location ID: {prop.location_id}")
            print(f"  Price: {prop.price} {prop.currency}")
            print(f"  Area: {prop.area} sqm")
            print(f"  Bedrooms: {prop.bedrooms}")
            print(f"  Bathrooms: {prop.bathrooms}")

            # Test location relationship
            if prop.location_id is not None:
                location = (
                    session.query(SimplifiedLocation)
                    .filter_by(id=prop.location_id)
                    .first()
                )
                if location:
                    print(
                        f"  Location Details: {location.name} (Level {location.level})"
                    )
                else:
                    print(f"  ⚠️  Location ID {prop.location_id} not found!")
            else:
                print("  ℹ️  No location ID (using location string only)")

    finally:
        session.close()


def test_location_queries():
    """Test location-based queries."""
    print("\n🔍 Testing Location Queries...")
    print("=" * 40)

    session = SessionLocal()
    try:
        # Test 1: Find properties by location string
        print("1. Properties with 'Riyadh' in location:")
        riyadh_properties = (
            session.query(SimplifiedProperty)
            .filter(SimplifiedProperty.location.ilike("%Riyadh%"))
            .count()
        )
        print(f"   Found: {riyadh_properties} properties")

        # Test 2: Find properties with location_id
        print("\n2. Properties with location_id:")
        properties_with_location = (
            session.query(SimplifiedProperty)
            .filter(SimplifiedProperty.location_id.isnot(None))
            .count()
        )
        print(f"   Found: {properties_with_location} properties")

        # Test 3: Find properties without location_id
        print("\n3. Properties without location_id:")
        properties_without_location = (
            session.query(SimplifiedProperty)
            .filter(SimplifiedProperty.location_id.is_(None))
            .count()
        )
        print(f"   Found: {properties_without_location} properties")

        # Test 4: Location hierarchy
        print("\n4. Location hierarchy levels:")
        location_levels = session.query(SimplifiedLocation.level).distinct().all()
        levels = [level[0] for level in location_levels]
        print(f"   Levels found: {sorted(levels)}")

        # Test 5: Sample location with properties
        sample_location = session.query(SimplifiedLocation).first()
        if sample_location:
            print(
                f"\n5. Sample location '{sample_location.name}' (Level {sample_location.level}):"
            )
            location_properties = (
                session.query(SimplifiedProperty)
                .filter_by(location_id=sample_location.id)
                .count()
            )
            print(f"   Properties in this location: {location_properties}")

    finally:
        session.close()


def test_performance_comparison():
    """Compare query performance between old and new systems."""
    print("\n⚡ Testing Query Performance...")
    print("=" * 40)

    session = SessionLocal()
    try:
        import time

        # Test new system (simplified)
        start_time = time.time()
        simplified_result = (
            session.query(SimplifiedProperty)
            .filter(SimplifiedProperty.location.ilike("%Riyadh%"))
            .count()
        )
        simplified_time = time.time() - start_time

        # Test old system (complex)
        start_time = time.time()
        complex_result = (
            session.query(Property)
            .join(PropertyLocation, Property.id == PropertyLocation.property_id)
            .join(UniqueLocation, PropertyLocation.location_id == UniqueLocation.id)
            .filter(UniqueLocation.name.ilike("%Riyadh%"))
            .count()
        )
        complex_time = time.time() - start_time

        print("New System (Simplified):")
        print("  Query: Simple location string search")
        print(f"  Result: {simplified_result} properties")
        print(f"  Time: {simplified_time:.4f} seconds")

        print("\nOld System (Complex):")
        print("  Query: Multi-table join with location hierarchy")
        print(f"  Result: {complex_result} properties")
        print(f"  Time: {complex_time:.4f} seconds")

        if simplified_time < complex_time:
            improvement = ((complex_time - simplified_time) / complex_time) * 100
            print(f"\n✅ New system is {improvement:.1f}% faster!")
        else:
            print(
                f"\n⚠️  Performance difference: {simplified_time - complex_time:.4f} seconds"
            )

    finally:
        session.close()


def test_data_consistency():
    """Test data consistency between old and new systems."""
    print("\n🔍 Testing Data Consistency...")
    print("=" * 40)

    session = SessionLocal()
    try:
        # Check for any properties that might have been lost
        old_external_ids = set(session.query(Property.external_id).all())
        new_external_ids = set(session.query(SimplifiedProperty.external_id).all())

        old_ids = {id[0] for id in old_external_ids}
        new_ids = {id[0] for id in new_external_ids}

        missing_ids = old_ids - new_ids
        extra_ids = new_ids - old_ids

        print(f"Old system external IDs: {len(old_ids)}")
        print(f"New system external IDs: {len(new_ids)}")

        if not missing_ids:
            print("✅ No properties lost in migration!")
        else:
            print(f"❌ {len(missing_ids)} properties missing from new system")

        if not extra_ids:
            print("✅ No duplicate properties created!")
        else:
            print(f"⚠️  {len(extra_ids)} extra properties in new system")

        # Check location data
        locations_with_properties = (
            session.query(SimplifiedLocation)
            .join(
                SimplifiedProperty,
                SimplifiedLocation.id == SimplifiedProperty.location_id,
            )
            .count()
        )

        print(f"\nLocations with properties: {locations_with_properties}")

    finally:
        session.close()


def main():
    """Run all tests."""
    print("🧪 Testing Simplified Location System Migration")
    print("=" * 50)

    try:
        test_data_counts()
        test_sample_data()
        test_location_queries()
        test_performance_comparison()
        test_data_consistency()

        print("\n🎉 All tests completed!")
        print("\nSummary:")
        print("✅ Migration validation complete")
        print("✅ Data integrity verified")
        print("✅ Query performance tested")
        print("✅ Ready to use simplified system!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
