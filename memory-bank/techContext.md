# Technical Context: Bayut.sa Property Scraper

## Technology Stack

### Core Technologies

#### Python 3.9+
- **Version**: Python 3.9 or higher
- **Purpose**: Primary programming language
- **Features**: Async/await support, type hints, dataclasses
- **Rationale**: Excellent async support, rich ecosystem, strong typing

#### aiohttp 3.12.14
- **Purpose**: Async HTTP client/server framework
- **Features**: Async HTTP requests, session management, connection pooling
- **Configuration**: Custom headers, timeout handling, retry logic
- **Usage**: Primary HTTP client for Algolia API communication

#### asyncio 3.4.3
- **Purpose**: Asynchronous I/O support
- **Features**: Event loop, coroutines, concurrent execution
- **Usage**: Core async functionality, rate limiting, batch processing

### Development Environment

#### Virtual Environment
- **Tool**: Python venv
- **Location**: `.venv/` directory
- **Activation**: `source .venv/bin/activate`
- **Script**: `activate_venv.sh` for easy activation
- **Benefits**: Isolated dependencies, reproducible environment

#### Package Management
- **Tool**: pip 25.1.1
- **File**: `requirements.txt`
- **Installation**: `pip install -r requirements.txt`
- **Upgrade**: `pip install --upgrade pip`

### Dependencies

#### Core Dependencies
```txt
aiohttp>=3.8.0
asyncio
typing-extensions>=4.0.0
```

#### Supporting Dependencies
- **aiohappyeyeballs**: 2.6.1 - DNS resolution optimization
- **aiosignal**: 1.4.0 - Signal handling for async operations
- **async-timeout**: 5.0.1 - Timeout management
- **attrs**: 25.3.0 - Data class utilities
- **frozenlist**: 1.7.0 - Immutable list implementation
- **idna**: 3.10 - Internationalized domain names
- **multidict**: 6.6.3 - Multi-value dictionary
- **propcache**: 0.3.2 - Property caching
- **yarl**: 1.20.1 - URL parsing and manipulation

## API Integration

### Algolia Search API
- **Base URL**: `https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries`
- **Application ID**: `LL8IZ711CS`
- **API Key**: `5b970b39b22a4ff1b99e5167696eef3f`
- **Index**: `bayut-sa-production-ads-city-level-score-ar`
- **Method**: POST
- **Content-Type**: application/json

### API Headers
```python
headers = {
    "X-Algolia-API-Key": "5b970b39b22a4ff1b99e5167696eef3f",
    "X-Algolia-Application-Id": "LL8IZ711CS",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}
```

### Request Structure
```python
payload = {
    "requests": [
        {
            "indexName": "bayut-sa-production-ads-city-level-score-ar",
            "params": f"query=&hitsPerPage={batch_size}&page={page_num}&filters={filters}&attributesToRetrieve={attributes}&attributesToHighlight={attributes}"
        }
    ]
}
```

## Data Models

### PropertyListing Dataclass
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
    extra_fields: Dict[str, Any]
```

### REGA Data Structure
```python
# Nested REGA information in extra_fields
extra_fields = {
    "rega_license_info_ad_license_number": "7200299856",
    "rega_location_city": {"ar": "الرياض", "en": "Riyadh"},
    "rega_property_specs_price": 1300000,
    "rega_license_info_start_date": "2024-09-20",
    "rega_license_info_end_date": "2025-09-20"
}
```

## Configuration

### Environment Variables
```bash
# Virtual environment
VIRTUAL_ENV=.venv
PATH=.venv/bin:$PATH

# Python path
PYTHONPATH=/Users/raedmund/Projects/Bayut_mapping
```

### Scraper Configuration
```python
# Default settings
DEFAULT_DELAY = 1.0  # seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 2.0
BATCH_SIZE = 25  # listings per page
MAX_PAGES = 100  # maximum pages to scrape
```

### Logging Configuration
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## File Structure

### Project Layout
```
Bayut_mapping/
├── .venv/                          # Virtual environment
├── memory-bank/                    # Project documentation
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   ├── activeContext.md
│   └── progress.md
├── bayut_scraper.py               # Original scraper
├── bayut_scraper_enhanced.py      # Enhanced scraper with REGA data
├── scrape_100_properties.py       # Demo script
├── test_scraper.py                # Test script
├── test_enhanced_scraper.py       # Enhanced scraper tests
├── requirements.txt               # Python dependencies
├── activate_venv.sh              # Virtual environment activation
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
└── curl_examples.md              # API usage examples
```

### Output Files
```
# Generated during scraping
100_properties.json              # Raw JSON output
100_properties_db_ready.json     # Database-ready format
test_enhanced_results.json       # Test results
enhanced_apartments_for_sale.json # Category-specific results
```

## Development Tools

### Code Quality
- **Type Hints**: Full type annotation support
- **Dataclasses**: Structured data models
- **Async/Await**: Modern Python async patterns
- **Error Handling**: Comprehensive exception management

### Testing
- **Manual Testing**: `test_scraper.py` and `test_enhanced_scraper.py`
- **Data Validation**: Property listing validation
- **API Testing**: Direct API endpoint testing
- **Integration Testing**: End-to-end scraping workflows

### Documentation
- **README.md**: Comprehensive project documentation
- **Memory Bank**: Structured project knowledge
- **Code Comments**: Inline documentation
- **API Examples**: curl_examples.md for direct API usage

## Performance Characteristics

### Async Performance
- **Concurrent Requests**: Multiple API calls simultaneously
- **Rate Limiting**: Configurable delays between requests
- **Batch Processing**: Efficient pagination handling
- **Memory Management**: Streaming for large datasets

### API Efficiency
- **Single Endpoint**: All queries through Algolia API
- **Structured Data**: Direct JSON parsing
- **Minimal Overhead**: No HTML parsing required
- **Caching Ready**: Easy to add response caching

### Scalability
- **Horizontal Scaling**: Multiple scraper instances
- **Vertical Scaling**: Increased batch sizes and concurrency
- **Resource Management**: Proper session cleanup
- **Error Recovery**: Robust retry mechanisms

## Security Considerations

### API Security
- **API Key Protection**: Secure header transmission
- **Rate Limiting**: Respectful API usage
- **Error Sanitization**: No sensitive data in logs
- **Input Validation**: Filter string sanitization

### Data Security
- **Local Storage**: All data stored locally
- **No External Services**: Self-contained operation
- **Encrypted Communication**: HTTPS for all API calls
- **Access Control**: File system permissions

## Deployment Considerations

### Environment Setup
```bash
# Production setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Monitoring
- **Logging**: Comprehensive error and info logging
- **Progress Tracking**: Real-time scraping progress
- **Error Reporting**: Detailed error messages
- **Performance Metrics**: Timing and success rates

### Maintenance
- **Dependency Updates**: Regular package updates
- **API Monitoring**: Detect endpoint changes
- **Data Validation**: Ensure ongoing data quality
- **Documentation Updates**: Keep guides current

## Integration Points

### Database Integration
- **PostgreSQL**: Compatible with existing `properties` table
- **JSONB Fields**: Support for nested REGA data
- **Bulk Insert**: Efficient database loading
- **Schema Mapping**: Direct field mapping

### File System Integration
- **JSON Export**: Multiple output formats
- **UTF-8 Encoding**: Proper Arabic text handling
- **File Naming**: Timestamped output files
- **Directory Structure**: Organized output storage

### External APIs
- **Algolia Search**: Primary data source
- **Rate Limiting**: Respectful API consumption
- **Error Handling**: Robust retry and recovery
- **Authentication**: Proper API key management 