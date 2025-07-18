# Bayut.sa Property Scraper

A comprehensive, efficient, and async Python scraper for Bayut.sa property listings using reverse-engineered Algolia API endpoints.

## Features

- **Async Scraping**: Efficient concurrent API requests using Python asyncio
- **Complete Data Capture**: All property fields including REGA (Real Estate General Authority) information
- **Flexible Filtering**: Support for various search criteria (category, purpose, location, price)
- **Production Ready**: Robust error handling, rate limiting, and data validation
- **Database Integration**: PostgreSQL-ready data with normalized schema
- **Code Quality**: Comprehensive linting and formatting tools

## Quick Start

### 1. Setup Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or use the convenience script
./activate_venv.sh

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Scraper

```bash
# Basic scraping (100 properties)
python bayut.py

# Or run the enhanced scraper
python src/bayut_scraper_enhanced.py
```

### 3. Check Code Quality

```bash
# Run all code quality checks
./scripts/lint.sh

# Format code automatically
./scripts/format.sh
```

## Code Quality Tools

This project uses a comprehensive set of code quality tools:

### **Primary Tools (Ruff-First Approach)**

- **Ruff**: Fast linter and formatter (10-100x faster than alternatives)
  - Linting: `ruff check src/ tests/ bayut.py`
  - Formatting: `ruff format src/ tests/ bayut.py`
  - Auto-fix: `ruff check --fix src/ tests/ bayut.py`

- **Black**: Backup formatter for consistency
  - Formatting: `black src/ tests/ bayut.py`

### **Additional Tools**

- **Flake8**: Comprehensive linting with additional rules
- **Vulture**: Dead code detection
- **Pytest**: Testing framework with async support

### **Why Ruff-First?**

1. **Speed**: Ruff is extremely fast (10-100x faster than other tools)
2. **Comprehensive**: Can handle both linting and formatting
3. **Auto-fix**: Automatically fixes many common issues
4. **Modern**: Built with Rust for performance
5. **Compatible**: Works well with Black formatting

### **Usage Examples**

```bash
# Quick format check
ruff format --check src/ tests/ bayut.py

# Quick lint check
ruff check src/ tests/ bayut.py

# Auto-fix issues
ruff check --fix src/ tests/ bayut.py

# Run all quality checks
./scripts/lint.sh

# Format all code
./scripts/format.sh
```

## Project Structure

```
Bayut/
├── src/                          # Source code
│   ├── bayut_scraper.py         # Original scraper
│   ├── bayut_scraper_enhanced.py # Enhanced scraper with REGA data
│   ├── models.py                # Data models
│   └── db_utils.py              # Database utilities
├── tests/                       # Test files
│   ├── test_scraper.py         # Basic scraper tests
│   └── test_enhanced_scraper.py # Enhanced scraper tests
├── scripts/                     # Utility scripts
│   ├── lint.sh                 # Code quality checks
│   └── format.sh               # Code formatting
├── memory-bank/                 # Project documentation
├── data/                        # Output data
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration
├── .flake8                     # Flake8 configuration
└── README.md                   # This file
```

## Configuration

### Code Quality Settings

The project is configured with:

- **Line Length**: 88 characters (Black standard)
- **Python Version**: 3.9+
- **Target Version**: py39
- **Quote Style**: Double quotes
- **Indent Style**: Spaces

### Key Configuration Files

- `pyproject.toml`: Main configuration for Ruff, Black, Vulture, and Pytest
- `.flake8`: Flake8-specific configuration
- `scripts/lint.sh`: Convenience script for all quality checks
- `scripts/format.sh`: Convenience script for code formatting

## Development Workflow

### 1. Before Committing

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all quality checks
./scripts/lint.sh

# If issues found, format code
./scripts/format.sh

# Run tests
pytest tests/ -v
```

### 2. Quick Development

```bash
# Just check formatting
ruff format --check src/ tests/ bayut.py

# Just check linting
ruff check src/ tests/ bayut.py

# Auto-fix common issues
ruff check --fix src/ tests/ bayut.py
```

### 3. Individual Tool Usage

```bash
# Ruff (recommended)
ruff check src/ tests/ bayut.py
ruff format src/ tests/ bayut.py

# Black (backup)
black src/ tests/ bayut.py

# Flake8 (comprehensive)
flake8 src/ tests/ bayut.py

# Vulture (dead code)
vulture src/ tests/ bayut.py

# Pytest (testing)
pytest tests/ -v
```

## API Integration

The scraper uses Bayut.sa's Algolia search API:

- **Base URL**: `https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries`
- **Application ID**: `LL8IZ711CS`
- **Index**: `bayut-sa-production-ads-city-level-score-ar`
- **Method**: POST with JSON payload

## Data Models

### PropertyListing

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

## Database Integration

The scraper prepares data for PostgreSQL with:

- **Normalized Schema**: Separate tables for agencies, agents, media, locations
- **JSONB Fields**: Flexible storage for REGA data
- **Bulk Insert**: Efficient database loading with upserts
- **Foreign Keys**: Proper relationships between tables

## Performance

- **Scraping Speed**: ~25 properties per minute
- **Rate Limiting**: 1-second delays between requests
- **Memory Usage**: Efficient async processing
- **Error Recovery**: Robust retry mechanisms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run code quality checks: `./scripts/lint.sh`
5. Format code: `./scripts/format.sh`
6. Run tests: `pytest tests/ -v`
7. Submit a pull request

## License

This project is for educational and research purposes. Please respect Bayut.sa's terms of service.

## Support

For issues and questions:
1. Check the memory-bank/ documentation
2. Review the test files for usage examples
3. Check the curl_examples.md for API details 