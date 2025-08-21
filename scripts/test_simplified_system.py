#!/usr/bin/env python3
"""
Test script to verify the simplified system works correctly.
This tests the renamed tables and updated models.
"""

import logging
import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from src.db_utils import get_property_stats
from src.models import (
    Agency,
    Agent,
    Document,
    Location,
    Media,
    PaymentPlan,
    Project,
    Property,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://raedmund@localhost:5432/bayut")


def test_table_structure():
    """Test that the table structure is correct."""
    logger.info("Testing table structure...")

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Check that tables exist
        result = conn.execute(
            text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('properties', 'locations', 'agencies', 'agents', 'projects', 'media', 'payment_plans', 'documents')
            ORDER BY table_name
        """)
        )

        tables = [row[0] for row in result.fetchall()]
        expected_tables = [
            "agencies",
            "agents",
            "documents",
            "locations",
            "media",
            "payment_plans",
            "projects",
            "properties",
        ]

        logger.info(f"Found tables: {tables}")
        logger.info(f"Expected tables: {expected_tables}")

        if set(tables) == set(expected_tables):
            logger.info("✅ All expected tables exist")
        else:
            logger.error("❌ Missing or extra tables found")
            return False

        # Check properties table structure
        result = conn.execute(
            text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'properties'
            ORDER BY ordinal_position
        """)
        )

        properties_columns = {row[0]: row[1] for row in result.fetchall()}
        expected_properties_columns = {
            "id": "integer",
            "external_id": "character varying",
            "title": "character varying",
            "title_ar": "character varying",
            "price": "double precision",
            "currency": "character varying",
            "location": "character varying",
            "location_id": "integer",
            "area": "double precision",
            "bedrooms": "integer",
            "bathrooms": "integer",
            "property_type": "character varying",
            "purpose": "character varying",
            "permit_number": "character varying",
            "is_verified": "boolean",
            "extra_fields": "json",
            "agency_id": "integer",
            "agent_id": "integer",
            "project_id": "integer",
        }

        logger.info("Properties table columns:")
        for col, dtype in properties_columns.items():
            logger.info(f"  {col}: {dtype}")

        if properties_columns == expected_properties_columns:
            logger.info("✅ Properties table structure is correct")
        else:
            logger.error("❌ Properties table structure mismatch")
            return False

        # Check locations table structure
        result = conn.execute(
            text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'locations'
            ORDER BY ordinal_position
        """)
        )

        locations_columns = {row[0]: row[1] for row in result.fetchall()}
        expected_locations_columns = {
            "id": "integer",
            "external_id": "character varying",
            "name": "character varying",
            "name_ar": "character varying",
            "slug": "character varying",
            "level": "integer",
            "parent_id": "integer",
            "latitude": "double precision",
            "longitude": "double precision",
        }

        logger.info("Locations table columns:")
        for col, dtype in locations_columns.items():
            logger.info(f"  {col}: {dtype}")

        if locations_columns == expected_locations_columns:
            logger.info("✅ Locations table structure is correct")
        else:
            logger.error("❌ Locations table structure mismatch")
            return False

        return True


def test_data_integrity():
    """Test that data integrity is maintained."""
    logger.info("Testing data integrity...")

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Check property count
        property_count = session.query(Property).count()
        logger.info(f"Total properties: {property_count}")

        if property_count == 0:
            logger.warning("⚠️ No properties found in database")
            return True

        # Check location count
        location_count = session.query(Location).count()
        logger.info(f"Total locations: {location_count}")

        # Check agency count
        agency_count = session.query(Agency).count()
        logger.info(f"Total agencies: {agency_count}")

        # Check agent count
        agent_count = session.query(Agent).count()
        logger.info(f"Total agents: {agent_count}")

        # Check project count
        project_count = session.query(Project).count()
        logger.info(f"Total projects: {project_count}")

        # Check media count
        media_count = session.query(Media).count()
        logger.info(f"Total media items: {media_count}")

        # Check payment plans count
        payment_plans_count = session.query(PaymentPlan).count()
        logger.info(f"Total payment plans: {payment_plans_count}")

        # Check documents count
        documents_count = session.query(Document).count()
        logger.info(f"Total documents: {documents_count}")

        # Test a sample property
        sample_property = session.query(Property).first()
        if sample_property:
            logger.info(f"Sample property: {sample_property.title}")
            logger.info(f"  Location: {sample_property.location}")
            logger.info(f"  Price: {sample_property.price} {sample_property.currency}")
            logger.info(f"  Agency ID: {sample_property.agency_id}")
            logger.info(f"  Agent ID: {sample_property.agent_id}")
            logger.info(f"  Project ID: {sample_property.project_id}")

            # Test relationships
            if sample_property.agency:
                logger.info(f"  Agency: {sample_property.agency.name}")
            if sample_property.agent:
                logger.info(f"  Agent: {sample_property.agent.name}")
            if sample_property.project:
                logger.info(f"  Project: {sample_property.project.name}")
            if sample_property.location_ref:
                logger.info(
                    f"  Canonical Location: {sample_property.location_ref.name}"
                )

        # Test location hierarchy
        root_locations = (
            session.query(Location).filter(Location.parent_id.is_(None)).all()
        )
        logger.info(f"Root locations: {len(root_locations)}")
        for loc in root_locations[:3]:  # Show first 3
            logger.info(f"  {loc.name} (level {loc.level})")
            children = (
                session.query(Location).filter(Location.parent_id == loc.id).all()
            )
            logger.info(f"    Children: {len(children)}")

        logger.info("✅ Data integrity check completed")
        return True

    except Exception as e:
        logger.error(f"❌ Error during data integrity check: {e}")
        return False
    finally:
        session.close()


def test_queries():
    """Test common queries to ensure they work."""
    logger.info("Testing common queries...")

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Test property queries
        properties_in_riyadh = (
            session.query(Property).filter(Property.location.ilike("%riyadh%")).count()
        )
        logger.info(f"Properties in Riyadh: {properties_in_riyadh}")

        # Test price range queries
        expensive_properties = (
            session.query(Property).filter(Property.price > 1000000).count()
        )
        logger.info(f"Properties over 1M SAR: {expensive_properties}")

        # Test agency queries
        from sqlalchemy import func

        top_agencies = (
            session.query(Agency)
            .join(Property)
            .group_by(Agency.id)
            .order_by(func.count(Property.id).desc())
            .limit(5)
            .all()
        )

        logger.info("Top agencies by property count:")
        for agency in top_agencies:
            prop_count = (
                session.query(Property).filter(Property.agency_id == agency.id).count()
            )
            logger.info(f"  {agency.name}: {prop_count} properties")

        # Test location queries
        cities = session.query(Location).filter(Location.level == 1).all()
        logger.info(f"Cities in database: {len(cities)}")
        for city in cities[:3]:  # Show first 3
            logger.info(f"  {city.name}")

        logger.info("✅ Query tests completed")
        return True

    except Exception as e:
        logger.error(f"❌ Error during query tests: {e}")
        return False
    finally:
        session.close()


def test_stats():
    """Test the statistics function."""
    logger.info("Testing statistics function...")

    try:
        stats = get_property_stats()

        logger.info("Database Statistics:")
        logger.info(f"  Properties: {stats['properties']['total']}")
        logger.info(f"  With Agency: {stats['properties']['with_agency']}")
        logger.info(f"  With Agent: {stats['properties']['with_agent']}")
        logger.info(f"  With Project: {stats['properties']['with_project']}")
        logger.info(f"  Agencies: {stats['related_data']['agencies']}")
        logger.info(f"  Agents: {stats['related_data']['agents']}")
        logger.info(f"  Projects: {stats['related_data']['projects']}")
        logger.info(f"  Media: {stats['related_data']['media']}")
        logger.info(f"  Payment Plans: {stats['related_data']['payment_plans']}")
        logger.info(f"  Documents: {stats['related_data']['documents']}")

        logger.info("✅ Statistics function works correctly")
        return True

    except Exception as e:
        logger.error(f"❌ Error during statistics test: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("Starting simplified system tests...")

    tests = [
        ("Table Structure", test_table_structure),
        ("Data Integrity", test_data_integrity),
        ("Queries", test_queries),
        ("Statistics", test_stats),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'=' * 50}")
        logger.info(f"Running {test_name} Test")
        logger.info(f"{'=' * 50}")

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    logger.info(f"\n{'=' * 50}")
    logger.info("Test Summary")
    logger.info(f"{'=' * 50}")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! The simplified system is working correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
