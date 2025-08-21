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
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Change Tracking │    │ Price History   │    │ Location-Based  │
│                 │    │                 │    │ Analysis        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Enhanced Architecture with Change Tracking
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Scheduler      │───▶│ Change Detector │───▶│ Enhanced Scraper│
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Notification    │    │ State Manager   │    │ Price Analyzer  │
│ System          │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Price History   │    │ Property Changes│    │ Location Data   │
│ Database        │    │ Database        │    │ Database        │
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

#### 4. Change Detection System (New)
- **Purpose**: Track changes in property listings over time
- **Pattern**: State management with comparison algorithms
- **Responsibilities**: Change detection, state persistence, event generation

#### 5. Price History Tracker (New)
- **Purpose**: Maintain temporal price data for analysis
- **Pattern**: Time-series data management
- **Features**: Location-based tracking and analysis

#### 6. Location-Based Analyzer (New)
- **Purpose**: Provide location-specific analysis capabilities
- **Pattern**: Location hierarchy analysis
- **Features**: Cross-location comparisons, market insights, trend analysis

## Change Tracking Patterns

### 1. State Management Pattern
**Purpose**: Maintain previous scraping state for comparison
**Implementation**:
```python
class StateManager:
    def __init__(self, db_session):
        self.session = db_session
        self.cache = {}
    
    async def get_previous_state(self, location: str) -> Dict:
        """Get previous scraping state for a location"""
        # Query database for last known state
        pass
    
    async def update_state(self, location: str, new_data: List[Dict]):
        """Update state with new scraping results"""
        # Store new state and trigger comparison
        pass
```

### 2. Change Detection Pattern
**Purpose**: Identify new, updated, and removed listings
**Implementation**:
```python
class ChangeDetector:
    def detect_changes(self, previous: Dict, current: List[Dict]) -> List[ChangeEvent]:
        """Detect changes between previous and current state"""
        changes = []
        
        # Find new listings
        current_ids = {item['external_id'] for item in current}
        previous_ids = set(previous.keys())
        
        new_ids = current_ids - previous_ids
        removed_ids = previous_ids - current_ids
        
        # Find updated listings
        for item in current:
            if item['external_id'] in previous:
                if self._has_changes(previous[item['external_id']], item):
                    changes.append(ChangeEvent('updated', item))
            else:
                changes.append(ChangeEvent('new', item))
        
        return changes
```

### 3. Temporal Data Pattern
**Purpose**: Store and query time-series price data
**Implementation**:
```python
class PriceHistoryTracker:
    def __init__(self, db_session):
        self.session = db_session
    
    async def record_prices(self, location: str, listings: List[Dict]):
        """Record current prices for historical tracking"""
        for listing in listings:
            price_record = PriceHistory(
                property_id=listing['external_id'],
                location_id=listing['location_id'],
                asking_price=listing['price'],
                captured_at=datetime.utcnow()
            )
            self.session.add(price_record)
        
        await self.session.commit()
    
    async def get_price_trends(self, location: str, days: int = 30):
        """Get price trends for a location over time"""
        # Query price history with temporal analysis
        pass
```

### 4. Location-Based Analysis Pattern
**Purpose**: Provide location-specific market analysis
**Implementation**:
```python
class LocationAnalyzer:
    def __init__(self, db_session):
        self.session = db_session
    
    async def analyze_location_trends(self, location: str, days: int = 30):
        """Analyze price trends for a specific location"""
        # Get price history for the location
        price_data = await self._get_location_price_history(location, days)
        
        # Calculate trends and insights
        trends = self._calculate_trends(price_data)
        
        return trends
    
    async def compare_locations(self, locations: List[str]):
        """Compare multiple locations"""
        comparisons = {}
        for i, loc1 in enumerate(locations):
            for loc2 in locations[i+1:]:
                comparison = await self._compare_two_locations(loc1, loc2)
                comparisons[f"{loc1}_vs_{loc2}"] = comparison
        
        return comparisons
    
    def create_location_report(self, location: str):
        """Create comprehensive market report for a location"""
        # Generate location-specific insights
        pass
```

### 5. Notification Pattern
**Purpose**: Alert users to significant changes
**Implementation**:
```python
class NotificationSystem:
    def __init__(self, config: Dict):
        self.thresholds = config.get('thresholds', {})
        self.channels = config.get('channels', [])
    
    async def process_changes(self, changes: List[ChangeEvent]):
        """Process changes and send notifications"""
        for change in changes:
            if self._should_notify(change):
                await self._send_notification(change)
    
    def _should_notify(self, change: ChangeEvent) -> bool:
        """Determine if change warrants notification"""
        if change.type == 'price_change':
            return abs(change.price_change_percent) > self.thresholds['price_change']
        return True
```

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

### 4. Location-Based Change Tracking
**Decision**: Use location-based tracking approach
**Rationale**:
- Natural market boundaries align with user behavior
- Matches Bayut's existing location structure
- Efficient storage and querying
- Easy to understand and maintain

**Implementation**:
```python
class LocationBasedChangeTracker:
    def __init__(self, location_analyzer, change_detector):
        self.location_analyzer = location_analyzer
        self.change_detector = change_detector
    
    async def track_location_changes(self, location: str):
        """Track changes for a specific location"""
        # Location-based tracking
        location_changes = await self.change_detector.detect_changes(location)
        
        # Location-specific analysis
        location_insights = await self.location_analyzer.analyze_location_trends(location)
        
        return {
            'location_changes': location_changes,
            'location_insights': location_insights
        }
```

### 5. Virtual Environment Isolation
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

### 5. State Pattern (New)
**Usage**: Change detection state management
```python
class ChangeDetectionState:
    def __init__(self):
        self.previous_state = {}
        self.current_state = {}
    
    def update_state(self, new_data: List[Dict]):
        self.previous_state = self.current_state.copy()
        self.current_state = {item['id']: item for item in new_data}
    
    def detect_changes(self) -> List[ChangeEvent]:
        # Compare previous and current state
        pass
```

### 6. Command Pattern (New)
**Usage**: Notification and alert handling
```python
class NotificationCommand:
    def __init__(self, change_event: ChangeEvent, channel: str):
        self.change_event = change_event
        self.channel = channel
    
    async def execute(self):
        if self.channel == 'email':
            await self._send_email()
        elif self.channel == 'webhook':
            await self._send_webhook()
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

### 4. Change Detection Flow (New)
```
Scrape Data → Load Previous State → Compare States → Detect Changes → Generate Events → Store History → Send Notifications
```

### 5. Location Analysis Flow (New)
```
Location Data → Extract Location Info → Location-Based Analysis → Cross-location Comparison → Generate Insights
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

### 4. Change Tracking Configuration (New)
```python
# Change tracking settings
CHANGE_TRACKING_CONFIG = {
    'polling_interval': 3600,  # 1 hour
    'price_change_threshold': 5.0,  # 5% price change
    'locations': ['الرياض', 'جدة', 'الدمام'],
    'notification_channels': ['email', 'webhook']
}
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

### 4. Change Detection Error Handling (New)
```python
class ChangeDetectionError(Exception):
    """Base exception for change detection errors"""
    pass

class StateCorruptionError(ChangeDetectionError):
    """Raised when state data is corrupted"""
    pass

def safe_change_detection(previous_state: Dict, current_data: List[Dict]):
    try:
        return detect_changes(previous_state, current_data)
    except StateCorruptionError:
        logging.error("State corruption detected, resetting state")
        return reset_state_and_detect(current_data)
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

### 4. Change Detection Optimization (New)
```python
class OptimizedChangeDetector:
    def __init__(self):
        self.cache = {}
        self.index = {}
    
    def detect_changes_optimized(self, previous: Dict, current: List[Dict]):
        """Optimized change detection using indexing"""
        # Build index for fast lookups
        current_index = {item['id']: item for item in current}
        
        # Fast comparison using set operations
        current_ids = set(current_index.keys())
        previous_ids = set(previous.keys())
        
        new_ids = current_ids - previous_ids
        removed_ids = previous_ids - current_ids
        
        return {
            'new': [current_index[id] for id in new_ids],
            'removed': [previous[id] for id in removed_ids],
            'updated': self._find_updates(previous, current_index)
        }
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

### 3. Change Tracking Integration (New)
```python
class ChangeTrackingIntegration:
    def __init__(self, scraper, change_detector, notification_system):
        self.scraper = scraper
        self.change_detector = change_detector
        self.notification_system = notification_system
    
    async def track_and_notify(self, location: str):
        """Complete change tracking workflow"""
        # Scrape current data
        current_data = await self.scraper.scrape_by_location(location)
        
        # Detect changes
        changes = await self.change_detector.detect_changes(location, current_data)
        
        # Send notifications
        if changes:
            await self.notification_system.notify(changes)
        
        return changes
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

### 4. Change Tracking Security (New)
```python
class SecureChangeTracker:
    def __init__(self):
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
    
    def encrypt_sensitive_data(self, data: Dict) -> Dict:
        """Encrypt sensitive data before storage"""
        # Implement encryption for sensitive fields
        return encrypted_data
    
    def validate_change_authenticity(self, change: ChangeEvent) -> bool:
        """Validate that change is authentic and not tampered"""
        # Implement change validation logic
        return True
``` 