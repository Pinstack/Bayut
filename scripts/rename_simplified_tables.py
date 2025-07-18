#!/usr/bin/env python3
"""
Script to rename simplified tables to standard names.
This replaces the old complex location system with the new simplified one.
"""

import logging
from sqlalchemy import text, create_engine
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.simplified_models import Base

# Database URL from environment or default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://raedmund@localhost:5432/bayut")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rename_tables():
    """Rename simplified tables to standard names."""
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        logger.info("Starting table rename process...")
        
        # Step 1: Drop old complex tables (after confirming data is migrated)
        logger.info("Dropping old complex tables...")
        conn.execute(text("DROP TABLE IF EXISTS property_locations CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS unique_locations CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS properties CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS locations CASCADE"))
        
        # Step 2: Rename simplified tables to standard names
        logger.info("Renaming simplified tables to standard names...")
        conn.execute(text("ALTER TABLE simplified_properties RENAME TO properties"))
        conn.execute(text("ALTER TABLE simplified_locations RENAME TO locations"))
        
        # Step 3: Update sequences if they exist
        logger.info("Updating sequences...")
        try:
            conn.execute(text("ALTER SEQUENCE simplified_properties_id_seq RENAME TO properties_id_seq"))
        except Exception as e:
            logger.warning(f"Could not rename properties sequence: {e}")
            
        try:
            conn.execute(text("ALTER SEQUENCE simplified_locations_id_seq RENAME TO locations_id_seq"))
        except Exception as e:
            logger.warning(f"Could not rename locations sequence: {e}")
        
        # Step 4: Update foreign key constraints
        logger.info("Updating foreign key constraints...")
        conn.execute(text("""
            ALTER TABLE properties 
            DROP CONSTRAINT IF EXISTS simplified_properties_location_id_fkey
        """))
        
        conn.execute(text("""
            ALTER TABLE properties 
            ADD CONSTRAINT properties_location_id_fkey 
            FOREIGN KEY (location_id) REFERENCES locations(id)
        """))
        
        # Step 5: Update indexes
        logger.info("Updating indexes...")
        conn.execute(text("""
            ALTER INDEX IF EXISTS simplified_properties_pkey 
            RENAME TO properties_pkey
        """))
        
        conn.execute(text("""
            ALTER INDEX IF EXISTS simplified_locations_pkey 
            RENAME TO locations_pkey
        """))
        
        conn.execute(text("""
            ALTER INDEX IF EXISTS simplified_locations_name_key 
            RENAME TO locations_name_key
        """))
        
        conn.execute(text("""
            ALTER INDEX IF EXISTS simplified_locations_parent_id_key 
            RENAME TO locations_parent_id_key
        """))
        
        logger.info("Table rename completed successfully!")
        
        # Step 6: Verify the changes
        logger.info("Verifying table structure...")
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('properties', 'locations', 'agencies', 'agents', 'media', 'payment_plans', 'documents')
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result.fetchall()]
        logger.info(f"Available tables: {tables}")
        
        # Check properties table structure
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'properties'
            ORDER BY ordinal_position
        """))
        
        logger.info("Properties table structure:")
        for row in result.fetchall():
            logger.info(f"  {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
        
        # Check locations table structure
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'locations'
            ORDER BY ordinal_position
        """))
        
        logger.info("Locations table structure:")
        for row in result.fetchall():
            logger.info(f"  {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")

def main():
    """Main function."""
    try:
        rename_tables()
        logger.info("✅ Table rename completed successfully!")
    except Exception as e:
        logger.error(f"❌ Error during table rename: {e}")
        raise

if __name__ == "__main__":
    main() 