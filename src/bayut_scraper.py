#!/usr/bin/env python3
"""
Bayut.sa Property Scraper using Algolia API
Efficient, async, batch scraping of all property listings and nested data
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AlgoliaConfig:
    """Algolia API configuration for Bayut.sa"""
    app_id: str = "LL8IZ711CS"
    api_key: str = "5b970b39b22a4ff1b99e5167696eef3f"
    index_name: str = "bayut-sa-production-ads-city-level-score-ar"
    base_url: str = "https://ll8iz711cs-dsn.algolia.net/1/indexes"
    
    # Headers for Algolia API
    headers: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {
                "X-Algolia-Application-Id": self.app_id,
                "X-Algolia-API-Key": self.api_key,
                "X-Algolia-Agent": "Algolia for JavaScript (3.35.1); Browser (lite)",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

@dataclass
class PropertyListing:
    """Property listing data structure"""
    objectID: str
    title: str
    price: Optional[int]
    location: str
    area: Optional[float]
    rooms: Optional[int]
    baths: Optional[int]
    category: str
    purpose: str
    coverPhoto: Optional[str]
    photoCount: Optional[int]
    description: Optional[str]
    agency: Optional[str]
    contactName: Optional[str]
    phoneNumber: Optional[str]
    isVerified: bool
    createdAt: Optional[str]
    updatedAt: Optional[str]
    slug: Optional[str]
    externalID: Optional[str]
    geography: Optional[Dict]
    extraFields: Optional[Dict]
    project: Optional[Dict]
    paymentPlans: Optional[List]
    documents: Optional[List]

class BayutScraper:
    """Main scraper class for Bayut.sa using Algolia API"""
    
    def __init__(self, config: Optional[AlgoliaConfig] = None):
        self.config = config or AlgoliaConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.total_listings = 0
        self.processed_listings = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_listings(
        self,
        query: str = "",
        filters: str = "",
        page: int = 0,
        hits_per_page: int = 25,
        facets: Optional[List[str]] = None,
        attributes_to_retrieve: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search property listings using Algolia API
        
        Args:
            query: Search query string
            filters: Algolia filter string (e.g., "purpose:for-sale AND category:apartments")
            page: Page number (0-based)
            hits_per_page: Number of results per page
            facets: Facets to retrieve
            attributes_to_retrieve: Specific attributes to retrieve
            
        Returns:
            Dict containing search results
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        # Default attributes to retrieve (all available fields)
        if attributes_to_retrieve is None:
            attributes_to_retrieve = [
                "state", "type", "agency", "area", "baths", "category", 
                "additionalCategories", "contactName", "externalID", "sourceID", 
                "id", "location", "objectID", "phoneNumber", "coverPhoto", 
                "photoCount", "price", "product", "productLabel", "purpose", 
                "geography", "permitNumber", "referenceNumber", "rentFrequency", 
                "rooms", "slug", "slug_l1", "title", "title_l1", "createdAt", 
                "updatedAt", "ownerID", "isVerified", "propertyTour", 
                "verification", "completionDetails", "completionStatus", 
                "furnishingStatus", "coverVideo", "videoCount", "description", 
                "description_l1", "descriptionTranslated", "descriptionTranslated_l1", 
                "floorPlanID", "panoramaCount", "hasMatchingFloorPlans", 
                "photoIDs", "reactivatedAt", "hidePrice", "extraFields", 
                "projectNumber", "locationPurposeTier", "hasRedirectionLink", 
                "ownerAgent", "hasEmail", "plotArea", "offplanDetails", 
                "paymentPlans", "paymentPlanSummaries", "project", 
                "availabilityStatus", "userExternalID", "units", "unitCategories", 
                "downPayment", "clips", "contactMethodAvailability", 
                "agentAdStoriesCount", "isProjectOwned", "documents"
            ]
        
        # Default facets
        if facets is None:
            facets = ["*"]
        
        # Construct the search request body
        search_body = {
            "requests": [
                {
                    "indexName": self.config.index_name,
                    "query": query,
                    "params": f"hitsPerPage={hits_per_page}&page={page}&facets={','.join(facets)}&attributesToRetrieve={','.join(attributes_to_retrieve)}"
                }
            ]
        }
        
        # Add filters if provided
        if filters:
            search_body["requests"][0]["params"] += f"&filters={filters}"
        
        url = f"{self.config.base_url}/*/queries"
        
        try:
            async with self.session.post(
                url,
                headers=self.config.headers,
                json=search_body,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error during search: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            raise
    
    def parse_listing(self, hit: Dict[str, Any]) -> PropertyListing:
        """Parse a single listing from Algolia response"""
        return PropertyListing(
            objectID=hit.get("objectID", ""),
            title=hit.get("title", ""),
            price=hit.get("price"),
            location=hit.get("location", ""),
            area=hit.get("area"),
            rooms=hit.get("rooms"),
            baths=hit.get("baths"),
            category=hit.get("category", ""),
            purpose=hit.get("purpose", ""),
            coverPhoto=hit.get("coverPhoto"),
            photoCount=hit.get("photoCount"),
            description=hit.get("description"),
            agency=hit.get("agency"),
            contactName=hit.get("contactName"),
            phoneNumber=hit.get("phoneNumber"),
            isVerified=hit.get("isVerified", False),
            createdAt=hit.get("createdAt"),
            updatedAt=hit.get("updatedAt"),
            slug=hit.get("slug"),
            externalID=hit.get("externalID"),
            geography=hit.get("geography"),
            extraFields=hit.get("extraFields"),
            project=hit.get("project"),
            paymentPlans=hit.get("paymentPlans"),
            documents=hit.get("documents")
        )
    
    async def scrape_all_listings(
        self,
        filters: str = "",
        max_pages: Optional[int] = None,
        batch_size: int = 25,
        delay_between_requests: float = 0.5
    ) -> List[PropertyListing]:
        """
        Scrape all property listings with pagination
        
        Args:
            filters: Algolia filter string
            max_pages: Maximum number of pages to scrape (None for all)
            batch_size: Number of results per page
            delay_between_requests: Delay between requests in seconds
            
        Returns:
            List of all property listings
        """
        all_listings = []
        page = 0
        
        logger.info(f"Starting to scrape listings with filters: {filters}")
        
        while True:
            try:
                logger.info(f"Scraping page {page + 1}...")
                
                # Search for listings
                response = await self.search_listings(
                    filters=filters,
                    page=page,
                    hits_per_page=batch_size
                )
                
                # Extract results
                if "results" in response and len(response["results"]) > 0:
                    result = response["results"][0]
                    hits = result.get("hits", [])
                    total_hits = result.get("nbHits", 0)
                    
                    if page == 0:
                        self.total_listings = total_hits
                        logger.info(f"Total listings found: {total_hits}")
                    
                    if not hits:
                        logger.info("No more hits found, stopping pagination")
                        break
                    
                    # Parse listings
                    page_listings = [self.parse_listing(hit) for hit in hits]
                    all_listings.extend(page_listings)
                    self.processed_listings += len(page_listings)
                    
                    logger.info(f"Page {page + 1}: {len(hits)} listings (Total: {self.processed_listings}/{self.total_listings})")
                    
                    # Check if we've reached the end
                    if len(hits) < batch_size:
                        logger.info("Reached last page")
                        break
                    
                    # Check max pages limit
                    if max_pages and page >= max_pages - 1:
                        logger.info(f"Reached maximum pages limit ({max_pages})")
                        break
                    
                    page += 1
                    
                    # Delay between requests to be respectful
                    if delay_between_requests > 0:
                        await asyncio.sleep(delay_between_requests)
                        
                else:
                    logger.warning("No results in response")
                    break
                    
            except Exception as e:
                logger.error(f"Error scraping page {page + 1}: {e}")
                break
        
        logger.info(f"Scraping completed. Total listings scraped: {len(all_listings)}")
        return all_listings
    
    async def scrape_by_category_and_purpose(
        self,
        category: str = "apartments",
        purpose: str = "for-sale",
        location: Optional[str] = None,
        max_pages: Optional[int] = None
    ) -> List[PropertyListing]:
        """
        Scrape listings by category and purpose with optional location filter
        
        Args:
            category: Property category (apartments, villas, etc.)
            purpose: Property purpose (for-sale, for-rent)
            location: Optional location filter
            max_pages: Maximum pages to scrape
            
        Returns:
            List of property listings
        """
        filters = f"category:{category} AND purpose:{purpose}"
        
        if location:
            filters += f" AND location:{location}"
        
        return await self.scrape_all_listings(filters=filters, max_pages=max_pages)
    
    def save_listings_to_json(self, listings: List[PropertyListing], filename: str):
        """Save listings to JSON file"""
        data = {
            "scraped_at": datetime.now().isoformat(),
            "total_listings": len(listings),
            "listings": [vars(listing) for listing in listings]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(listings)} listings to {filename}")

async def main():
    """Main function demonstrating the scraper usage"""
    
    # Example usage
    async with BayutScraper() as scraper:
        
        # Example 1: Scrape all apartments for sale in Saudi Arabia
        logger.info("=== Example 1: Scraping apartments for sale ===")
        apartments_for_sale = await scraper.scrape_by_category_and_purpose(
            category="apartments",
            purpose="for-sale",
            max_pages=2  # Limit for demo
        )
        
        # Save results
        scraper.save_listings_to_json(apartments_for_sale, "apartments_for_sale.json")
        
        # Example 2: Scrape with custom filters
        logger.info("=== Example 2: Scrape with custom filters ===")
        custom_filters = "purpose:for-sale AND category:villas AND price>=1000000"
        custom_listings = await scraper.scrape_all_listings(
            filters=custom_filters,
            max_pages=1  # Limit for demo
        )
        
        scraper.save_listings_to_json(custom_listings, "custom_filters.json")
        
        # Example 3: Get detailed listing information
        logger.info("=== Example 3: Getting detailed listing info ===")
        if apartments_for_sale:
            sample_listing = apartments_for_sale[0]
            logger.info(f"Sample listing: {sample_listing.title}")
            logger.info(f"Price: {sample_listing.price}")
            logger.info(f"Location: {sample_listing.location}")
            logger.info(f"Area: {sample_listing.area}")
            logger.info(f"Rooms: {sample_listing.rooms}")
            logger.info(f"Baths: {sample_listing.baths}")
            logger.info(f"Verified: {sample_listing.isVerified}")

if __name__ == "__main__":
    asyncio.run(main()) 