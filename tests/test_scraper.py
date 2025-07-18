#!/usr/bin/env python3
"""
Test script for Bayut.sa scraper
"""

import pytest

from src.bayut_scraper import EnhancedBayutScraper


@pytest.mark.asyncio
async def test_basic_scraping():
    """Test basic scraping functionality"""
    print("🧪 Testing Bayut.sa Scraper...")

    try:
        async with EnhancedBayutScraper() as scraper:
            print("✅ Scraper initialized successfully")

            # Test single page scraping
            print("📊 Testing single page scraping...")
            listings = await scraper.scrape_by_category_and_purpose(
                category="apartments", purpose="for-sale", max_pages=1
            )

            print(f"✅ Scraped {len(listings)} listings")

            if listings:
                # Show sample listing
                sample = listings[0]
                print("\n📋 Sample Listing:")
                print(f"   Title: {sample.title}")
                print(f"   Price: {sample.price}")
                print(f"   Location: {sample.location}")
                print(f"   Area: {sample.area}")
                print(f"   Rooms: {sample.bedrooms}")
                print(f"   Baths: {sample.bathrooms}")
                print(f"   Verified: {sample.is_verified}")

                # Save test results
                scraper.save_listings_to_json(listings, "test_results.json")
                print("\n💾 Saved test results to test_results.json")

            return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


@pytest.mark.asyncio
async def test_filtering():
    """Test filtering functionality"""
    print("\n🔍 Testing filtering...")

    try:
        async with EnhancedBayutScraper() as scraper:
            # Test custom filters
            custom_filters = "purpose:for-sale AND category:apartments"
            listings = await scraper.scrape_all_listings(
                filters=custom_filters, max_pages=1
            )

            print(f"✅ Filter test: {len(listings)} listings found")
            return True

    except Exception as e:
        print(f"❌ Filter test failed: {e}")
        return False
