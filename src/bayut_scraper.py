#!/usr/bin/env python3
"""
Enhanced Bayut.sa Property Scraper using Algolia API
Efficient, async, batch scraping of all property listings and nested data
Including comprehensive REGA information and bilingual support
"""

import asyncio
import json
import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from pythonjsonlogger.json import JsonFormatter

# Configure structured JSON logging
logHandler = logging.StreamHandler()
formatter = JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
logHandler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)


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
                "Accept": "application/json",
            }


@dataclass
class PropertyListing:
    """Enhanced property listing data structure matching the JSON file format"""

    # Basic identification
    external_id: str
    objectID: Optional[str] = None

    # Basic property information
    title: str = ""
    title_ar: Optional[str] = None
    description: str = ""
    description_ar: Optional[str] = None

    # Property classification
    property_type: str = ""
    property_type_ar: Optional[str] = None
    purpose: str = ""

    # Financial information
    price: Optional[int] = None
    currency: str = "SAR"

    # Property specifications
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    area_unit: str = "sqm"

    # Location information
    location: str = ""
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_hierarchy: Optional[List[Dict]] = None

    # Agency and agent information
    agency_name: Optional[str] = None
    agency_name_ar: Optional[str] = None
    agent_name: Optional[str] = None
    agent_name_ar: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None

    # Media
    photo_url: Optional[str] = None
    photo_count: Optional[int] = None

    # Regulatory information
    permit_number: Optional[str] = None
    reference_number: Optional[str] = None

    # Property status
    furnishing_status: Optional[str] = None
    completion_status: Optional[str] = None
    is_verified: bool = False

    # Timestamps
    scraped_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # Additional data (from Algolia)
    geography: Optional[Dict] = None
    extra_fields: Optional[Dict] = None
    raw_data: Optional[Dict] = None
    project: Optional[Dict] = None
    payment_plans: Optional[List] = None
    documents: Optional[List] = None


class EnhancedBayutScraper:
    """Enhanced scraper class for Bayut.sa using Algolia API"""

    def __init__(
        self,
        config: Optional[AlgoliaConfig] = None,
        max_retries: int = 5,
        backoff_factor: float = 1.5,
        concurrency: int = 1,
        delay_between_requests: float = 0.5,
    ):
        self.config = config or AlgoliaConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.total_listings = 0
        self.processed_listings = 0
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.concurrency = concurrency
        self.delay_between_requests = delay_between_requests
        self._semaphore = asyncio.Semaphore(concurrency)

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
        attributes_to_retrieve: Optional[List[str]] = None,
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
                "state",
                "type",
                "agency",
                "area",
                "baths",
                "category",
                "additionalCategories",
                "contactName",
                "externalID",
                "sourceID",
                "id",
                "location",
                "objectID",
                "phoneNumber",
                "coverPhoto",
                "photoCount",
                "price",
                "product",
                "productLabel",
                "purpose",
                "geography",
                "permitNumber",
                "referenceNumber",
                "rentFrequency",
                "rooms",
                "slug",
                "slug_l1",
                "title",
                "title_l1",
                "createdAt",
                "updatedAt",
                "ownerID",
                "isVerified",
                "propertyTour",
                "verification",
                "completionDetails",
                "completionStatus",
                "furnishingStatus",
                "coverVideo",
                "videoCount",
                "description",
                "description_l1",
                "descriptionTranslated",
                "descriptionTranslated_l1",
                "floorPlanID",
                "panoramaCount",
                "hasMatchingFloorPlans",
                "photoIDs",
                "reactivatedAt",
                "hidePrice",
                "extraFields",
                "projectNumber",
                "locationPurposeTier",
                "hasRedirectionLink",
                "ownerAgent",
                "hasEmail",
                "plotArea",
                "offplanDetails",
                "paymentPlans",
                "paymentPlanSummaries",
                "project",
                "availabilityStatus",
                "userExternalID",
                "units",
                "unitCategories",
                "downPayment",
                "clips",
                "contactMethodAvailability",
                "agentAdStoriesCount",
                "isProjectOwned",
                "documents",
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
                    "params": f"hitsPerPage={hits_per_page}&page={page}&facets={','.join(facets)}&attributesToRetrieve={','.join(attributes_to_retrieve)}",
                }
            ]
        }

        # Add filters if provided
        if filters:
            search_body["requests"][0]["params"] += f"&filters={filters}"

        url = f"{self.config.base_url}/*/queries"

        attempt = 0
        while True:
            try:
                async with self.session.post(
                    url,
                    headers=self.config.headers,
                    json=search_body,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                attempt += 1
                if attempt > self.max_retries:
                    logger.error(f"Max retries exceeded for page {page}: {e}")
                    raise
                sleep_time = self.backoff_factor ** (attempt - 1)
                logger.warning(
                    f"Request failed (attempt {attempt}/{self.max_retries}): {e}. Retrying in {sleep_time:.1f}s..."
                )
                await asyncio.sleep(sleep_time)
            except Exception as e:
                logger.error(f"Unexpected error during search: {e}")
                raise

    def parse_listing(self, hit: Dict[str, Any]) -> PropertyListing:
        """Parse a single listing from Algolia response with enhanced field mapping"""

        # Extract location hierarchy from location array
        location_hierarchy = None
        if isinstance(hit.get("location"), list):
            location_hierarchy = hit.get("location")
            # Extract city from location hierarchy
            city = None
            if location_hierarchy:
                for loc in location_hierarchy:
                    if loc.get("level") == 1:  # City level
                        city = loc.get("name")
                        break
            else:
                city = None
        else:
            city = None

        # Extract geography coordinates
        geography = hit.get("geography", {})
        latitude = geography.get("lat") if geography else None
        longitude = geography.get("lng") if geography else None

        # Extract extra fields (REGA data)
        extra_fields = hit.get("extraFields", {})

        # Extract photo URL from coverPhoto
        photo_url = hit.get("coverPhoto")

        # Extract permit and reference numbers
        permit_number = hit.get("permitNumber")
        reference_number = hit.get("referenceNumber")

        # Extract status information
        completion_status = hit.get("completionStatus")
        furnishing_status = hit.get("furnishingStatus")

        # Extract contact information
        phone = hit.get("phoneNumber")
        whatsapp = None  # Not directly available in Algolia, might be in extraFields

        # Extract agency and agent information
        agency_name = hit.get("agency")
        agent_name = hit.get("contactName")

        return PropertyListing(
            # Basic identification
            external_id=hit.get("externalID", ""),
            objectID=hit.get("objectID"),
            # Basic property information
            title=hit.get("title", ""),
            title_ar=hit.get("title_l1"),  # English title as Arabic equivalent
            description=hit.get("description", ""),
            description_ar=hit.get(
                "description_l1"
            ),  # English description as Arabic equivalent
            # Property classification
            property_type=hit.get("category", ""),
            property_type_ar=hit.get("type"),  # Use type as Arabic equivalent
            purpose=hit.get("purpose", ""),
            # Financial information
            price=hit.get("price"),
            currency="SAR",  # Default for Saudi Arabia
            # Property specifications
            bedrooms=hit.get("rooms"),
            bathrooms=hit.get("baths"),
            area=hit.get("area"),
            area_unit="sqm",
            # Location information
            location=hit.get("location", ""),
            city=city,
            latitude=latitude,
            longitude=longitude,
            location_hierarchy=location_hierarchy,
            # Agency and agent information
            agency_name=agency_name,
            agency_name_ar=agency_name,  # Same as English for now
            agent_name=agent_name,
            agent_name_ar=agent_name,  # Same as English for now
            phone=phone,
            whatsapp=whatsapp,
            # Media
            photo_url=photo_url,
            photo_count=hit.get("photoCount"),
            # Regulatory information
            permit_number=permit_number,
            reference_number=reference_number,
            # Property status
            furnishing_status=furnishing_status,
            completion_status=completion_status,
            is_verified=hit.get("isVerified", False),
            # Timestamps
            scraped_at=datetime.now().isoformat(),
            created_at=hit.get("createdAt"),
            updated_at=hit.get("updatedAt"),
            # Additional data
            geography=geography,
            extra_fields=extra_fields,
            raw_data=hit,  # Store complete raw data
            project=hit.get("project"),
            payment_plans=hit.get("paymentPlans"),
            documents=hit.get("documents"),
        )

    async def scrape_all_listings(
        self,
        filters: str = "",
        max_pages: Optional[int] = None,
        batch_size: int = 25,
        delay_between_requests: Optional[float] = None,
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

        delay = (
            delay_between_requests
            if delay_between_requests is not None
            else self.delay_between_requests
        )

        while True:
            try:
                logger.info(f"Scraping page {page + 1}...")

                # Search for listings
                # Use semaphore for future concurrency support
                async with self._semaphore:
                    response = await self.search_listings(
                        filters=filters, page=page, hits_per_page=batch_size
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

                    logger.info(
                        f"Page {page + 1}: {len(hits)} listings (Total: {self.processed_listings}/{self.total_listings})"
                    )

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
                    if delay > 0:
                        await asyncio.sleep(delay)

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
        max_pages: Optional[int] = None,
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
        """Save listings to JSON file in the same format as your existing file"""
        # Convert dataclass objects to dictionaries
        listings_data = []
        for listing in listings:
            listing_dict = vars(listing)
            # Remove None values to match your JSON format
            listing_dict = {k: v for k, v in listing_dict.items() if v is not None}
            listings_data.append(listing_dict)

        # Save as array of objects (matching your format)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(listings_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(listings)} listings to {filename}")

    def save_listings_to_database_format(
        self, listings: List[PropertyListing], filename: str
    ):
        """Save listings in a format ready for database insertion"""
        data = {
            "scraped_at": datetime.now().isoformat(),
            "total_listings": len(listings),
            "listings": [],
        }

        for listing in listings:
            # Convert to database-ready format
            db_listing = {
                "external_id": listing.external_id,
                "title": listing.title,
                "title_ar": listing.title_ar,
                "description": listing.description,
                "description_ar": listing.description_ar,
                "property_type": listing.property_type,
                "property_type_ar": listing.property_type_ar,
                "purpose": listing.purpose,
                "price": listing.price,
                "currency": listing.currency,
                "bedrooms": listing.bedrooms,
                "bathrooms": listing.bathrooms,
                "area": listing.area,
                "area_unit": listing.area_unit,
                "location": listing.location,
                "city": listing.city,
                "latitude": listing.latitude,
                "longitude": listing.longitude,
                "agency_name": listing.agency_name,
                "agency_name_ar": listing.agency_name_ar,
                "agent_name": listing.agent_name,
                "agent_name_ar": listing.agent_name_ar,
                "phone": listing.phone,
                "whatsapp": listing.whatsapp,
                "photo_url": listing.photo_url,
                "photo_count": listing.photo_count,
                "permit_number": listing.permit_number,
                "reference_number": listing.reference_number,
                "furnishing_status": listing.furnishing_status,
                "completion_status": listing.completion_status,
                "is_verified": listing.is_verified,
                "scraped_at": listing.scraped_at,
                "created_at": listing.created_at,
                "updated_at": listing.updated_at,
                # JSONB fields
                "amenities": (
                    listing.extra_fields.get("amenities")
                    if listing.extra_fields
                    else None
                ),
                "images": (
                    listing.extra_fields.get("images") if listing.extra_fields else None
                ),
                "license_info": (
                    {
                        "permit_number": listing.permit_number,
                        "reference_number": listing.reference_number,
                        "rega_data": listing.extra_fields,
                    }
                    if listing.extra_fields
                    else None
                ),
                "location_details": {
                    "hierarchy": listing.location_hierarchy,
                    "geography": listing.geography,
                    "latitude": listing.latitude,
                    "longitude": listing.longitude,
                },
                "property_details": {
                    "raw_data": listing.raw_data,
                    "project": listing.project,
                    "payment_plans": listing.payment_plans,
                    "documents": listing.documents,
                },
            }

            # Remove None values
            db_listing = {k: v for k, v in db_listing.items() if v is not None}
            data["listings"].append(db_listing)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(listings)} listings in database format to {filename}")


def clean_for_json(data):
    def _clean(obj, seen=None):
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return None  # Remove circular reference
        seen.add(obj_id)
        if isinstance(obj, Mapping):
            return {k: _clean(v, seen) for k, v in obj.items()}
        elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
            return [_clean(i, seen) for i in obj]
        try:
            json.dumps(obj)
            return obj
        except Exception:
            return str(obj)

    return _clean(data)


def map_api_to_db(hit):
    # Flatten location
    loc = hit.get("location")
    if isinstance(loc, list) and loc:
        location_val = loc[-1].get("name") or loc[-1].get("externalID") or str(loc[-1])
    elif isinstance(loc, dict):
        location_val = loc.get("name") or loc.get("externalID") or str(loc)
    else:
        location_val = loc if isinstance(loc, str) else None
    # Flatten property_type
    pt = hit.get("property_type")
    if isinstance(pt, list) and pt:
        property_type_val = (
            pt[-1].get("name") or pt[-1].get("externalID") or str(pt[-1])
        )
    elif isinstance(pt, dict):
        property_type_val = pt.get("name") or pt.get("externalID") or str(pt)
    else:
        property_type_val = pt if isinstance(pt, str) else None
    return {
        "external_id": hit.get("external_id"),
        "title": hit.get("title") or hit.get("title_ar"),
        "price": hit.get("price"),
        "currency": hit.get("currency"),
        "location": location_val,
        "area": hit.get("area"),
        "bedrooms": hit.get("bedrooms"),
        "bathrooms": hit.get("bathrooms"),
        "property_type": property_type_val,
        "permit_number": hit.get("permit_number"),
        "is_verified": hit.get("is_verified"),
        "extra_fields": clean_for_json(
            {
                k: v
                for k, v in hit.items()
                if k
                not in {
                    "external_id",
                    "title",
                    "title_ar",
                    "price",
                    "currency",
                    "location",
                    "area",
                    "bedrooms",
                    "bathrooms",
                    "property_type",
                    "permit_number",
                    "is_verified",
                }
            }
        ),
    }


if __name__ == "__main__":
    from db_utils import bulk_insert_properties

    async def main():
        async with EnhancedBayutScraper() as scraper:
            listings = await scraper.scrape_all_listings(
                filters="",  # No filters: get all listings (for sale, for lease, etc.)
                max_pages=None,  # No limit: scrape all pages
            )
            if listings is None or not listings:
                print("No listings found.")
                return
            # Use explicit mapping for each listing
            prepared = [map_api_to_db(listing.__dict__) for listing in listings]
            bulk_insert_properties(prepared)
            print(f"Inserted {len(prepared)} properties into the database.")

    asyncio.run(main())
