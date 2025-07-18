# Bayut.sa Property Scraper

A comprehensive, efficient, and async Python scraper for Bayut.sa property listings using reverse-engineered Algolia API endpoints.

## 🎯 Features

- **Efficient API-based scraping** using Algolia search API
- **Async/await support** for high-performance batch scraping
- **Comprehensive data extraction** including all property details
- **Flexible filtering** by category, purpose, location, price, etc.
- **Pagination support** for scraping all available listings
- **Rate limiting** to be respectful to the API
- **JSON export** with structured data
- **Type hints** for better code maintainability
- **Complete REGA information** including all regulatory data
- **Bilingual support** (Arabic and English)

## 🚀 Quick Start

### Virtual Environment Setup

1. **Create and activate virtual environment:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Or use the provided script
./activate_venv.sh
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the scraper:**
```bash
# Scrape 100 properties (demo)
python src/scrape_100_properties.py

# Or run the enhanced scraper directly
python src/bayut_scraper_enhanced.py
```

### Alternative Setup (without virtual environment)

1. Clone this repository:
```bash
git clone <repository-url>
cd Bayut_mapping
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Run the scraper:
```bash
python3 src/scrape_100_properties.py
```

## 📁 Project Structure

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
├── src/                           # Source code
│   ├── __init__.py
│   ├── bayut_scraper.py          # Original scraper
│   ├── bayut_scraper_enhanced.py # Enhanced scraper with REGA data
│   └── scrape_100_properties.py  # Demo script
├── tests/                         # Test files
│   ├── __init__.py
│   ├── test_scraper.py
│   └── test_enhanced_scraper.py
├── data/                          # Data files
│   ├── output/                    # Scraper output
│   │   ├── 100_properties.json
│   │   └── 100_properties_db_ready.json
│   └── samples/                   # Sample data
│       ├── bayut_properties_full_20250718_075737.json
│       └── test_enhanced_results.json
├── requirements.txt               # Python dependencies
├── activate_venv.sh              # Virtual environment activation
├── .gitignore                    # Git ignore rules
├── .cursorrules                  # Project intelligence
└── README.md                     # Project documentation
```

## 📊 Data Structure

The scraper extracts comprehensive property data including:

- **Basic Info**: Title, price, location, area, rooms, baths
- **Property Details**: Category, purpose, description, photos
- **Contact Info**: Agency, contact name, phone number
- **Verification**: Is verified, verification details
- **Additional Data**: Geography, payment plans, documents, project info
- **Timestamps**: Created/updated dates
- **Media**: Photo count, video count, floor plans
- **REGA Information**: Complete regulatory and license data
- **Bilingual Content**: Arabic and English field variants

## 🔧 Usage Examples

### Basic Usage

```python
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bayut_scraper_enhanced import EnhancedBayutScraper

async def main():
    async with EnhancedBayutScraper() as scraper:
        # Scrape apartments for sale
        listings = await scraper.scrape_by_category_and_purpose(
            category="apartments",
            purpose="for-sale",
            max_pages=5
        )
        
        # Save to JSON
        scraper.save_listings_to_json(listings, "apartments_for_sale.json")

asyncio.run(main())
```

### Advanced Filtering

```python
# Custom filters
custom_filters = "purpose:for-sale AND category:villas AND price>=1000000"
listings = await scraper.scrape_all_listings(
    filters=custom_filters,
    max_pages=10
)

# Location-specific search
listings = await scraper.scrape_by_category_and_purpose(
    category="apartments",
    purpose="for-rent",
    location="الرياض",  # Riyadh
    max_pages=5
)
```

### Batch Processing

```python
# Scrape multiple categories
categories = ["apartments", "villas", "townhouses"]
purposes = ["for-sale", "for-rent"]

for category in categories:
    for purpose in purposes:
        listings = await scraper.scrape_by_category_and_purpose(
            category=category,
            purpose=purpose,
            max_pages=3
        )
        
        filename = f"{category}_{purpose}.json"
        scraper.save_listings_to_json(listings, filename)
```

## 🔍 API Details

### Algolia Configuration

- **Application ID**: `LL8IZ711CS`
- **API Key**: `5b970b39b22a4ff1b99e5167696eef3f`
- **Index**: `bayut-sa-production-ads-city-level-score-ar`
- **Endpoint**: `https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries`

### Available Filters

- `category`: apartments, villas, townhouses, etc.
- `purpose`: for-sale, for-rent
- `location`: City or area name
- `price`: Price range (e.g., `price>=1000000`)
- `rooms`: Number of rooms
- `baths`: Number of bathrooms
- `area`: Property area
- `isVerified`: Verification status

### Filter Examples

```python
# Price range
"price>=500000 AND price<=2000000"

# Multiple categories
"category:(apartments OR villas)"

# Location and price
"location:الرياض AND price>=1000000"

# Verified properties only
"isVerified:true"

# Complex filter
"purpose:for-sale AND category:apartments AND location:جدة AND price>=500000 AND rooms>=2"
```

## 📈 Performance Optimization

### Rate Limiting

The scraper includes built-in rate limiting to be respectful to the API:

```python
# Customize delay between requests
listings = await scraper.scrape_all_listings(
    filters="purpose:for-sale",
    delay_between_requests=1.0  # 1 second delay
)
```

### Batch Size

Adjust the number of results per page:

```python
# Increase batch size for faster scraping
listings = await scraper.scrape_all_listings(
    filters="purpose:for-sale",
    batch_size=50  # Default is 25
)
```

### Concurrent Scraping

For maximum efficiency, you can run multiple scrapers concurrently:

```python
async def scrape_category(category: str, purpose: str):
    async with EnhancedBayutScraper() as scraper:
        return await scraper.scrape_by_category_and_purpose(
            category=category,
            purpose=purpose,
            max_pages=5
        )

# Run multiple scrapers concurrently
tasks = [
    scrape_category("apartments", "for-sale"),
    scrape_category("villas", "for-sale"),
    scrape_category("apartments", "for-rent")
]

results = await asyncio.gather(*tasks)
```

## 📁 Output Format

The scraper saves data in structured JSON format:

```json
[
  {
    "external_id": "87589812",
    "title": "دور علوي مودرن للبيع - مشروع الارين حي الروابي,الرياض",
    "title_ar": "Modern upper floor for sale - Al Arin project, Rawabi neighborhood, Riyadh",
    "price": 1300000,
    "currency": "SAR",
    "location": "الرياض",
    "area": 600.0,
    "bedrooms": 3,
    "bathrooms": 3,
    "property_type": "سكني",
    "purpose": "for-sale",
    "permit_number": "7200299856",
    "is_verified": false,
    "extra_fields": {
      "rega_license_info_ad_license_number": "7200299856",
      "rega_location_city": {"ar": "الرياض", "en": "Riyadh"},
      "rega_property_specs_price": 1300000,
      "rega_license_info_start_date": "2024-09-20",
      "rega_license_info_end_date": "2025-09-20"
    }
  }
]
```

## 🏛️ REGA Information

The scraper collects comprehensive Real Estate General Authority (REGA) data:

### License Information
- Advertisement license numbers
- FAL license numbers
- License start/end dates
- Expiry dates

### Location Details
- Building numbers
- Street names
- Postal codes
- Coordinates
- District information

### Property Specifications
- Area sizes
- Room counts
- Listing types
- Usage classifications

### Additional Information
- Deed numbers
- Plan numbers
- Utilities availability
- Guarantees and duration
- Marketing channels

## ⚠️ Important Notes

1. **Rate Limiting**: Always use appropriate delays between requests to avoid being blocked
2. **Terms of Service**: Ensure compliance with Bayut.sa's terms of service
3. **Data Usage**: Use scraped data responsibly and in accordance with applicable laws
4. **API Changes**: The Algolia API configuration may change; monitor for updates
5. **Virtual Environment**: Always use the virtual environment to avoid dependency conflicts

## 🛠️ Troubleshooting

### Common Issues

1. **Import Error**: Make sure to activate the virtual environment and install dependencies
2. **Connection Errors**: Check your internet connection and try again
3. **Rate Limiting**: Increase delay between requests if you encounter 429 errors
4. **Empty Results**: Verify your filter syntax and try broader filters

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Virtual Environment Issues

If you encounter issues with the virtual environment:

```bash
# Remove and recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 📝 License

This project is for educational purposes. Please ensure compliance with Bayut.sa's terms of service and applicable laws when using this scraper.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this scraper.

---

**Disclaimer**: This scraper is provided for educational purposes. Users are responsible for ensuring compliance with website terms of service and applicable laws. 