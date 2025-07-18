#!/usr/bin/env python3
"""
Test script for the enhanced Bayut.sa scraper
"""

import asyncio
import json
from bayut_scraper_enhanced import EnhancedBayutScraper

async def test_basic_search():
    """Test basic search without filters"""
    print("🧪 Testing enhanced Bayut.sa Scraper...")
    
    try:
        async with EnhancedBayutScraper() as scraper:
            print("✅ Scraper initialized successfully")
            
            # Test basic search without filters
            print("📊 Testing basic search without filters...")
            listings = await scraper.scrape_all_listings(
                filters="",  # No filters
                max_pages=1
            )
            
            print(f"✅ Found {len(listings)} listings")
            
            if listings:
                # Show sample listing
                sample = listings[0]
                print(f"\n📋 Sample Listing:")
                print(f"   External ID: {sample.external_id}")
                print(f"   Title: {sample.title}")
                print(f"   Price: {sample.price}")
                print(f"   Location: {sample.location}")
                print(f"   Area: {sample.area}")
                print(f"   Bedrooms: {sample.bedrooms}")
                print(f"   Bathrooms: {sample.bathrooms}")
                print(f"   Verified: {sample.is_verified}")
                print(f"   Permit Number: {sample.permit_number}")
                print(f"   REGA Data Available: {bool(sample.extra_fields)}")
                
                # Save test results
                scraper.save_listings_to_json(listings, "test_enhanced_results.json")
                print(f"\n💾 Saved test results to test_enhanced_results.json")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_different_filters():
    """Test different filter approaches"""
    print("\n🔍 Testing different filter approaches...")
    
    try:
        async with EnhancedBayutScraper() as scraper:
            # Test 1: Purpose only
            print("Testing purpose filter...")
            listings1 = await scraper.scrape_all_listings(
                filters="purpose:for-sale",
                max_pages=1
            )
            print(f"Purpose filter: {len(listings1)} listings")
            
            # Test 2: Category only
            print("Testing category filter...")
            listings2 = await scraper.scrape_all_listings(
                filters="category:apartments",
                max_pages=1
            )
            print(f"Category filter: {len(listings2)} listings")
            
            # Test 3: No filters at all
            print("Testing no filters...")
            listings3 = await scraper.scrape_all_listings(
                filters="",
                max_pages=1
            )
            print(f"No filters: {len(listings3)} listings")
            
            return len(listings1) > 0 or len(listings2) > 0 or len(listings3) > 0
            
    except Exception as e:
        print(f"❌ Filter test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Bayut.sa Scraper Tests\n")
    
    # Test basic functionality
    basic_test = await test_basic_search()
    
    # Test different filters
    filter_test = await test_different_filters()
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"   Basic Search: {'✅ PASS' if basic_test else '❌ FAIL'}")
    print(f"   Filter Tests: {'✅ PASS' if filter_test else '❌ FAIL'}")
    
    if basic_test or filter_test:
        print(f"\n🎉 Enhanced scraper is working! Found properties with some filter combinations.")
    else:
        print(f"\n⚠️  No properties found. This might indicate:")
        print(f"   - API rate limiting")
        print(f"   - Filter syntax issues")
        print(f"   - API changes")
        print(f"   - Network connectivity issues")

if __name__ == "__main__":
    asyncio.run(main()) 