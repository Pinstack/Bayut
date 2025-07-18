#!/usr/bin/env python3
"""
Test script for Bayut.sa scraper
"""

import asyncio
import json
from bayut_scraper import BayutScraper

async def test_basic_scraping():
    """Test basic scraping functionality"""
    print("🧪 Testing Bayut.sa Scraper...")
    
    try:
        async with BayutScraper() as scraper:
            print("✅ Scraper initialized successfully")
            
            # Test single page scraping
            print("📊 Testing single page scraping...")
            listings = await scraper.scrape_by_category_and_purpose(
                category="apartments",
                purpose="for-sale",
                max_pages=1
            )
            
            print(f"✅ Scraped {len(listings)} listings")
            
            if listings:
                # Show sample listing
                sample = listings[0]
                print(f"\n📋 Sample Listing:")
                print(f"   Title: {sample.title}")
                print(f"   Price: {sample.price}")
                print(f"   Location: {sample.location}")
                print(f"   Area: {sample.area}")
                print(f"   Rooms: {sample.rooms}")
                print(f"   Baths: {sample.baths}")
                print(f"   Verified: {sample.isVerified}")
                
                # Save test results
                scraper.save_listings_to_json(listings, "test_results.json")
                print(f"\n💾 Saved test results to test_results.json")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_filtering():
    """Test filtering functionality"""
    print("\n🔍 Testing filtering...")
    
    try:
        async with BayutScraper() as scraper:
            # Test custom filters
            custom_filters = "purpose:for-sale AND category:apartments"
            listings = await scraper.scrape_all_listings(
                filters=custom_filters,
                max_pages=1
            )
            
            print(f"✅ Filter test: {len(listings)} listings found")
            return True
            
    except Exception as e:
        print(f"❌ Filter test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Bayut.sa Scraper Tests\n")
    
    # Test basic functionality
    basic_test = await test_basic_scraping()
    
    # Test filtering
    filter_test = await test_filtering()
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"   Basic Scraping: {'✅ PASS' if basic_test else '❌ FAIL'}")
    print(f"   Filtering: {'✅ PASS' if filter_test else '❌ FAIL'}")
    
    if basic_test and filter_test:
        print(f"\n🎉 All tests passed! The scraper is working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main()) 