# System Patterns: Bayut.sa Property Scraper

## Architecture Overview

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Script   │───▶│  Bayut Scraper  │───▶│  Algolia API    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   JSON Output   │    │  Data Models    │    │  Rate Limiting  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

#### 1. EnhancedBayutScraper Class
- **Purpose**: Main orchestrator for scraping operations
- **Pattern**: Async context manager with resource management
- **Responsibilities**: API communication, data parsing, rate limiting

#### 2. PropertyListing Dataclass
- **Purpose**: Structured data model for property information
- **Pattern**: Type-safe data container with comprehensive fields
- **Features**: Bilingual support, REGA data integration

#### 3. Algolia API Client
- **Purpose**: Direct communication with Bayut's search API
- **Pattern**: Async HTTP client with proper headers and authentication
- **Configuration**: Application ID, API key, index name

## Key Technical Decisions

### 1. API-Based Scraping
**Decision**: Use Algolia search API instead of web scraping
**Rationale**: 
- More reliable and efficient
- Less likely to break with UI changes
- Better performance and rate limiting control
- Access to structured data directly

**Implementation**:
```python
# Algolia API configuration
ALGOLIA_APP_ID = "LL8IZ711CS"
ALGOLIA_API_KEY = "5b970b39b22a4ff1b99e5167696eef3f"
ALGOLIA_INDEX = "bayut-sa-production-ads-city-level-score-ar"
```

### 2. Async Architecture
**Decision**: Use Python asyncio for concurrent operations
**Rationale**:
- Better performance for I/O-bound operations
- Efficient handling of multiple API requests
- Built-in rate limiting and error handling
- Scalable for large datasets

**Implementation**:
```python
async with EnhancedBayutScraper() as scraper:
    listings = await scraper.scrape_all_listings(
        filters="purpose:for-sale",
        max_pages=10
    )
```

### 3. Comprehensive Data Model
**Decision**: Extract all available fields including nested REGA data
**Rationale**:
- Complete data capture for analysis
- Future-proof for additional use cases
- Database schema compatibility
- Regulatory compliance tracking

**Implementation**:
```python
@dataclass
class PropertyListing:
    external_id: str
    title: str
    title_ar: str
    price: float
    currency: str
    location: str
    area: float
    bedrooms: int
    bathrooms: int
    property_type: str
    purpose: str
    permit_number: str
    is_verified: bool
    extra_fields: Dict[str, Any]  # REGA data
```

### 4. Virtual Environment Isolation
**Decision**: Use Python virtual environment for dependency management
**Rationale**:
- Isolated dependencies
- Reproducible environment
- Easy setup and deployment
- Version control compatibility

**Implementation**:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Design Patterns

### 1. Context Manager Pattern
**Usage**: Resource management for HTTP sessions
```python
async with EnhancedBayutScraper() as scraper:
    # Automatic session cleanup
    listings = await scraper.scrape_all_listings()
```

### 2. Builder Pattern
**Usage**: Flexible filter construction
```python
filters = "purpose:for-sale AND category:apartments AND price>=500000"
listings = await scraper.scrape_all_listings(filters=filters)
```

### 3. Strategy Pattern
**Usage**: Different export formats
```python
# JSON export
scraper.save_listings_to_json(listings, "output.json")

# Database-ready export
scraper.save_listings_to_json(listings, "db_ready.json", db_format=True)
```

### 4. Observer Pattern
**Usage**: Progress tracking and logging
```python
logging.info(f"Scraping page {page_num}...")
logging.info(f"Total listings found: {total_listings}")
```

## Data Flow Patterns

### 1. Request-Response Flow
```
User Request → Filter Construction → API Call → Response Parsing → Data Model → Export
```

### 2. Pagination Flow
```
Initial Request → Parse Total Count → Calculate Pages → Batch Requests → Aggregate Results
```

### 3. Error Handling Flow
```
API Call → Success/Error Check → Retry Logic → Fallback → Logging → User Notification
```

## Configuration Patterns

### 1. Environment-Based Configuration
```python
# API configuration
ALGOLIA_APP_ID = "LL8IZ711CS"
ALGOLIA_API_KEY = "5b970b39b22a4ff1b99e5167696eef3f"
ALGOLIA_INDEX = "bayut-sa-production-ads-city-level-score-ar"
```

### 2. Rate Limiting Configuration
```python
# Default delays
DEFAULT_DELAY = 1.0  # seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 2.0
```

### 3. Data Export Configuration
```python
# Export options
JSON_INDENT = 2
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
```

## Error Handling Patterns

### 1. Graceful Degradation
```python
try:
    response = await self.session.post(url, json=payload)
    response.raise_for_status()
except aiohttp.ClientError as e:
    logging.error(f"API request failed: {e}")
    return []
```

### 2. Retry Logic
```python
for attempt in range(MAX_RETRIES):
    try:
        return await self._make_request(url, payload)
    except Exception as e:
        if attempt == MAX_RETRIES - 1:
            raise
        await asyncio.sleep(RETRY_DELAY * (attempt + 1))
```

### 3. Data Validation
```python
def _validate_listing(self, listing_data: Dict[str, Any]) -> bool:
    required_fields = ['externalID', 'title', 'price']
    return all(field in listing_data for field in required_fields)
```

## Performance Patterns

### 1. Batch Processing
```python
# Process listings in batches
for i in range(0, len(listings), BATCH_SIZE):
    batch = listings[i:i + BATCH_SIZE]
    await self._process_batch(batch)
```

### 2. Rate Limiting
```python
# Respectful API usage
await asyncio.sleep(self.delay_between_requests)
```

### 3. Memory Management
```python
# Stream processing for large datasets
async def scrape_with_streaming(self, max_pages: int):
    for page in range(1, max_pages + 1):
        listings = await self._scrape_page(page)
        yield listings
```

## Integration Patterns

### 1. Database Integration
```python
# PostgreSQL-ready format
def prepare_for_database(self, listings: List[PropertyListing]) -> List[Dict]:
    return [
        {
            "external_id": listing.external_id,
            "title": listing.title,
            "price": listing.price,
            "rega_data": json.dumps(listing.extra_fields)
        }
        for listing in listings
    ]
```

### 2. File Export Integration
```python
# Multiple export formats
def save_listings_to_json(self, listings: List[PropertyListing], 
                         filename: str, db_format: bool = False):
    if db_format:
        data = self.prepare_for_database(listings)
    else:
        data = [asdict(listing) for listing in listings]
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

## Security Patterns

### 1. API Key Management
```python
# Secure API key usage
headers = {
    "X-Algolia-API-Key": ALGOLIA_API_KEY,
    "X-Algolia-Application-Id": ALGOLIA_APP_ID,
    "Content-Type": "application/json"
}
```

### 2. Input Validation
```python
# Validate user inputs
def _validate_filters(self, filters: str) -> bool:
    # Sanitize and validate filter strings
    return True  # Implement validation logic
```

### 3. Error Information Sanitization
```python
# Don't expose sensitive information in errors
except Exception as e:
    logging.error(f"Scraping failed: {str(e)}")
    # Don't log API keys or sensitive data
``` 