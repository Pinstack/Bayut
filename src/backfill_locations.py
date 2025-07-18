#!/usr/bin/env python3
"""
Location Normalization Backfill Script
Deduplicates locations and creates normalized location hierarchy
"""

import logging
from collections import defaultdict

from sqlalchemy.dialects.postgresql import insert

from db_utils import SessionLocal
from models import Location, PropertyLocation, UniqueLocation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backfill_normalized_locations():
    """Backfill unique_locations and property_locations tables"""
    session = SessionLocal()
    try:
        logger.info("Starting location normalization backfill...")

        # Step 1: Extract all unique locations from current locations table
        logger.info("Step 1: Extracting unique locations...")
        all_locations = session.query(Location).all()

        # Create a dictionary to track unique locations by (external_id, level)
        unique_locations_dict = {}
        location_hierarchy = defaultdict(list)

        for loc in all_locations:
            # Handle None levels by defaulting to 0
            level = loc.level if loc.level is not None else 0
            key = (loc.external_id, level)
            if key not in unique_locations_dict:
                unique_locations_dict[key] = {
                    "external_id": loc.external_id,
                    "name": loc.name,
                    "name_l1": loc.name_l1,
                    "slug": loc.slug,
                    "slug_l1": loc.slug_l1,
                    "level": level,
                }
                location_hierarchy[level].append(unique_locations_dict[key])

        logger.info(
            f"Found {len(unique_locations_dict)} unique locations across {len(location_hierarchy)} levels"
        )

        # Step 2: Insert unique locations and build hierarchy
        logger.info("Step 2: Inserting unique locations and building hierarchy...")
        location_id_map = {}  # Map (external_id, level) to database ID

        # Insert locations level by level (parent before children)
        for level in sorted(location_hierarchy.keys()):
            for loc_data in location_hierarchy[level]:
                # Find parent location if this level has a parent
                parent_id = None
                if level > 0:
                    # Try to find parent by looking at the slug hierarchy
                    if loc_data["slug"]:
                        parent_slug = "/".join(loc_data["slug"].split("/")[:-1])
                        if parent_slug:
                            # Find parent by slug
                            parent_location = (
                                session.query(UniqueLocation)
                                .filter(UniqueLocation.slug == parent_slug)
                                .first()
                            )
                            if parent_location:
                                parent_id = parent_location.id

                # Insert the location
                stmt = insert(UniqueLocation).values(
                    external_id=loc_data["external_id"],
                    name=loc_data["name"],
                    name_l1=loc_data["name_l1"],
                    slug=loc_data["slug"],
                    slug_l1=loc_data["slug_l1"],
                    level=loc_data["level"],
                    parent_id=parent_id,
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=["external_id", "level"],
                    set_={
                        "name": stmt.excluded.name,
                        "name_l1": stmt.excluded.name_l1,
                        "slug": stmt.excluded.slug,
                        "slug_l1": stmt.excluded.slug_l1,
                        "parent_id": stmt.excluded.parent_id,
                    },
                )
                session.execute(stmt)
                session.flush()

                # Get the inserted/updated location ID
                location = (
                    session.query(UniqueLocation)
                    .filter_by(
                        external_id=loc_data["external_id"], level=loc_data["level"]
                    )
                    .first()
                )

                if location:
                    location_id_map[(loc_data["external_id"], loc_data["level"])] = (
                        location.id
                    )

        logger.info(f"Inserted {len(location_id_map)} unique locations")

        # Step 3: Populate property_locations join table
        logger.info("Step 3: Populating property_locations join table...")
        property_location_count = 0

        for loc in all_locations:
            # Handle None levels by defaulting to 0
            level = loc.level if loc.level is not None else 0
            location_id = location_id_map.get((loc.external_id, level))
            if location_id:
                # Insert property-location relationship
                stmt = insert(PropertyLocation).values(
                    property_id=loc.property_id,
                    location_id=location_id,
                    hierarchy_level=level,
                )
                stmt = stmt.on_conflict_do_nothing()  # Avoid duplicates
                session.execute(stmt)
                property_location_count += 1

        session.commit()
        logger.info(
            f"Created {property_location_count} property-location relationships"
        )

        # Step 4: Validation and reporting
        logger.info("Step 4: Validating results...")

        unique_location_count = session.query(UniqueLocation).count()
        property_location_count = session.query(PropertyLocation).count()
        original_location_count = session.query(Location).count()

        logger.info("Validation Results:")
        logger.info(f"  Original location records: {original_location_count}")
        logger.info(f"  Unique locations: {unique_location_count}")
        logger.info(f"  Property-location relationships: {property_location_count}")
        logger.info(
            f"  Deduplication ratio: {original_location_count / unique_location_count:.1f}:1"
        )

        # Sample some unique locations
        sample_locations = session.query(UniqueLocation).limit(5).all()
        logger.info("Sample unique locations:")
        for loc in sample_locations:
            logger.info(f"  Level {loc.level}: {loc.name} ({loc.external_id})")

        logger.info("Location normalization backfill completed successfully!")

    except Exception as e:
        session.rollback()
        logger.error(f"Error during location normalization: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    backfill_normalized_locations()
