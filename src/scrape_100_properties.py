#!/usr/bin/env python3
"""
Demo script to scrape 100 properties from Bayut.sa
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bayut_scraper_enhanced import EnhancedBayutScraper

async def scrape_100_properties():
    """Scrape 100 properties using the enhanced scraper"""
    print("🚀 Starting to scrape 100 properties from Bayut.sa...")
    
    try:
        async with EnhancedBayutScraper() as scraper:
            print("✅ Enhanced scraper initialized successfully")
            
            # Calculate pages needed for 100 properties (25 per page)
            pages_needed = 4  # 4 pages * 25 properties = 100 properties
            
            print(f"📊 Scraping {pages_needed} pages to get 100 properties...")
            
            # Scrape properties without filters to get a broad sample
            listings = await scraper.scrape_all_listings(
                filters="",  # No filters to get all types
                max_pages=pages_needed,
                batch_size=25,
                delay_between_requests=0.5
            )
            
            print(f"✅ Successfully scraped {len(listings)} properties")
            
            if listings:
                # Show sample of the data
                print(f"\n📋 Sample Properties:")
                for i, listing in enumerate(listings[:3]):  # Show first 3
                    print(f"\n   Property {i+1}:")
                    print(f"     External ID: {listing.external_id}")
                    print(f"     Title: {listing.title}")
                    print(f"     Price: {listing.price} {listing.currency}")
                    print(f"     Location: {listing.city or listing.location}")
                    print(f"     Area: {listing.area} {listing.area_unit}")
                    print(f"     Bedrooms: {listing.bedrooms}, Bathrooms: {listing.bathrooms}")
                    print(f"     Property Type: {listing.property_type}")
                    print(f"     Purpose: {listing.purpose}")
                    print(f"     Verified: {listing.is_verified}")
                    print(f"     Permit Number: {listing.permit_number}")
                    print(f"     REGA Data: {'✅ Available' if listing.extra_fields else '❌ Not available'}")
                
                # Save results in both formats
                output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "output")
                os.makedirs(output_dir, exist_ok=True)
                
                scraper.save_listings_to_json(listings, os.path.join(output_dir, "100_properties.json"))
                scraper.save_listings_to_database_format(listings, os.path.join(output_dir, "100_properties_db_ready.json"))
                
                print(f"\n💾 Saved {len(listings)} properties to:")
                print(f"   - data/output/100_properties.json (JSON format)")
                print(f"   - data/output/100_properties_db_ready.json (Database format)")
                
                # Show summary statistics
                print(f"\n📊 Summary Statistics:")
                print(f"   Total Properties: {len(listings)}")
                print(f"   Properties with REGA Data: {sum(1 for l in listings if l.extra_fields)}")
                print(f"   Properties with Permit Numbers: {sum(1 for l in listings if l.permit_number)}")
                print(f"   Verified Properties: {sum(1 for l in listings if l.is_verified)}")
                
                # Price statistics
                prices = [l.price for l in listings if l.price]
                if prices:
                    print(f"   Average Price: {sum(prices) / len(prices):,.0f} SAR")
                    print(f"   Min Price: {min(prices):,.0f} SAR")
                    print(f"   Max Price: {max(prices):,.0f} SAR")
                
                # Property types
                property_types = {}
                for listing in listings:
                    prop_type = listing.property_type
                    property_types[prop_type] = property_types.get(prop_type, 0) + 1
                
                print(f"   Property Types: {dict(property_types)}")
                
                return True
            else:
                print("❌ No properties were scraped")
                return False
                
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return False

async def main():
    """Main function"""
    print("=" * 60)
    print("Bayut.sa Property Scraper - 100 Properties")
    print("=" * 60)
    
    success = await scrape_100_properties()
    
    if success:
        print(f"\n🎉 Successfully scraped 100 properties!")
        print(f"   Check the generated JSON files for the complete data.")
    else:
        print(f"\n⚠️  Failed to scrape properties. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main()) 