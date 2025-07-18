#!/usr/bin/env python3
"""
Bayut.sa Property Scraper CLI

A comprehensive command-line interface for scraping property listings
from Bayut.sa with database integration and data normalization.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from backfill_locations import backfill_normalized_locations
from bayut_scraper import EnhancedBayutScraper
from db_utils import SessionLocal, backfill_properties_to_normalized_tables
from models import Agency, Agent, Media, Property, PropertyLocation, UniqueLocation

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_environment():
    """Ensure virtual environment is activated and dependencies are available"""
    if not os.path.exists(".venv"):
        logger.error(
            "Virtual environment not found. Please run: python -m venv .venv && source .venv/bin/activate"
        )
        sys.exit(1)


def scrape_command(args):
    """Handle scraping commands"""

    async def run_scraper():
        scraper = EnhancedBayutScraper()

        if args.all:
            logger.info("Starting full scrape of all properties...")
            await scraper.scrape_all_listings()
        else:
            limit = args.limit or 100
            logger.info(f"Starting scrape with limit: {limit}")
            await scraper.scrape_listings(limit=limit)

    asyncio.run(run_scraper())


def db_backfill_command(args):
    """Handle database backfill commands"""
    logger.info("Starting database backfill...")
    backfill_properties_to_normalized_tables()
    logger.info("Database backfill completed!")


def db_normalize_locations_command(args):
    """Handle location normalization commands"""
    logger.info("Starting location normalization...")
    backfill_normalized_locations()
    logger.info("Location normalization completed!")


def db_status_command(args):
    """Show database status and statistics"""
    session = SessionLocal()
    try:
        # Get counts
        property_count = session.query(Property).count()
        agency_count = session.query(Agency).count()
        agent_count = session.query(Agent).count()
        media_count = session.query(Media).count()
        unique_location_count = session.query(UniqueLocation).count()
        property_location_count = session.query(PropertyLocation).count()

        # Calculate relationships
        properties_with_agency = (
            session.query(Property).filter(Property.agency_id.isnot(None)).count()
        )
        properties_with_agent = (
            session.query(Property).filter(Property.agent_id.isnot(None)).count()
        )

        print("\n" + "=" * 50)
        print("DATABASE STATUS")
        print("=" * 50)
        print(f"Properties: {property_count:,}")
        print(f"Agencies: {agency_count:,}")
        print(f"Agents: {agent_count:,}")
        print(f"Media Items: {media_count:,}")
        print(f"Unique Locations: {unique_location_count:,}")
        print(f"Property-Location Relationships: {property_location_count:,}")
        print(
            f"Properties with Agency: {properties_with_agency:,} ({properties_with_agency / property_count * 100:.1f}%)"
        )
        print(
            f"Properties with Agent: {properties_with_agent:,} ({properties_with_agent / property_count * 100:.1f}%)"
        )
        print("=" * 50)

    finally:
        session.close()


def info_command(args):
    """Show project information"""
    print("\n" + "=" * 50)
    print("BAYUT.SA PROPERTY SCRAPER")
    print("=" * 50)
    print("A comprehensive property scraper for Bayut.sa with database integration")
    print("\nFEATURES:")
    print("• Async scraping with rate limiting")
    print("• Complete REGA data capture")
    print("• Normalized database schema")
    print("• Location hierarchy optimization")
    print("• Agency and agent tracking")
    print("• Media and document management")
    print("\nUSAGE EXAMPLES:")
    print("  python bayut.py scrape --limit 100")
    print("  python bayut.py scrape --all")
    print("  python bayut.py db:backfill")
    print("  python bayut.py db:normalize-locations")
    print("  python bayut.py db:status")
    print("  python bayut.py info")
    print("=" * 50)


def test_command(args):
    """Run basic tests"""
    logger.info("Running basic tests...")

    # Test database connection
    try:
        session = SessionLocal()
        property_count = session.query(Property).count()
        logger.info(f"✅ Database connection: {property_count} properties found")
        session.close()
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

    # Test scraper initialization
    try:
        _ = EnhancedBayutScraper()
        logger.info("✅ Scraper initialization successful")
    except Exception as e:
        logger.error(f"❌ Scraper initialization failed: {e}")
        return False

    logger.info("✅ All tests passed!")
    return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Bayut.sa Property Scraper CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bayut.py scrape --limit 100
  python bayut.py scrape --all
  python bayut.py db:backfill
  python bayut.py db:normalize-locations
  python bayut.py db:status
  python bayut.py info
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape property listings")
    scrape_parser.add_argument(
        "--limit", type=int, help="Limit number of properties to scrape"
    )
    scrape_parser.add_argument(
        "--all", action="store_true", help="Scrape all available properties"
    )
    scrape_parser.set_defaults(func=scrape_command)

    # Database commands
    db_parser = subparsers.add_parser("db", help="Database operations")
    db_subparsers = db_parser.add_subparsers(
        dest="db_command", help="Database subcommands"
    )

    # db:backfill
    db_backfill_parser = db_subparsers.add_parser(
        "backfill", help="Backfill normalized tables"
    )
    db_backfill_parser.set_defaults(func=db_backfill_command)

    # db:normalize-locations
    db_normalize_parser = db_subparsers.add_parser(
        "normalize-locations", help="Normalize location data"
    )
    db_normalize_parser.set_defaults(func=db_normalize_locations_command)

    # db:status
    db_status_parser = db_subparsers.add_parser("status", help="Show database status")
    db_status_parser.set_defaults(func=db_status_command)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show project information")
    info_parser.set_defaults(func=info_command)

    # Test command
    test_parser = subparsers.add_parser("test", help="Run basic tests")
    test_parser.set_defaults(func=test_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Setup environment
    setup_environment()

    # Execute command
    try:
        if hasattr(args, "func"):
            args.func(args)
        else:
            logger.error(f"Unknown command: {args.command}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
