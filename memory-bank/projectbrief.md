# Project Brief: Bayut.sa Property Scraper

## Project Overview
A comprehensive, efficient, and async Python scraper for Bayut.sa property listings using reverse-engineered Algolia API endpoints.

## Core Requirements

### Primary Goals
1. **Efficient Data Collection**: Scrape property listings from Bayut.sa using their Algolia search API
2. **Complete Data Extraction**: Capture all available property data including REGA (Real Estate General Authority) information
3. **High Performance**: Use async/await patterns for concurrent scraping
4. **Production Ready**: Robust error handling, rate limiting, and data validation
5. **Database Integration**: Prepare data for PostgreSQL storage with proper schema mapping

### Technical Requirements
- **API-Based Scraping**: Use Algolia search API instead of web scraping
- **Async Architecture**: Leverage Python asyncio for concurrent requests
- **Comprehensive Data Model**: Extract all property fields including nested REGA data
- **Flexible Filtering**: Support various search criteria (category, purpose, location, price)
- **Pagination Support**: Handle large datasets with proper pagination
- **Rate Limiting**: Respect API limits to avoid being blocked
- **Data Export**: JSON output in both raw and database-ready formats

### Data Requirements
- **Property Details**: Title, price, location, area, rooms, bathrooms
- **REGA Information**: License numbers, regulatory data, permit information
- **Contact Information**: Agency details, contact names, phone numbers
- **Media**: Photo counts, video counts, floor plans
- **Verification**: Property verification status and details
- **Bilingual Support**: Arabic and English field variants
- **Timestamps**: Creation and update dates
- **Geographic Data**: Coordinates, addresses, postal codes

### Success Criteria
- Successfully scrape 100+ properties with complete data
- All REGA information captured and structured
- Data ready for PostgreSQL database insertion
- Robust error handling and logging
- Production-ready code with proper documentation

## Project Scope

### In Scope
- Reverse engineering Bayut.sa's Algolia API
- Building async Python scraper
- Data extraction and structuring
- JSON export functionality
- Database schema preparation
- Virtual environment setup
- Comprehensive documentation

### Out of Scope
- Web UI for the scraper
- Real-time monitoring dashboard
- Automated scheduling
- Email notifications
- Advanced analytics

## Key Constraints
- Must respect Bayut.sa's terms of service
- Rate limiting to avoid API blocks
- Data accuracy and completeness
- Code maintainability and documentation
- Virtual environment isolation

## Success Metrics
- **Data Completeness**: 100% of available fields captured
- **Performance**: Efficient scraping with minimal API calls
- **Reliability**: Robust error handling and recovery
- **Usability**: Clear documentation and easy setup
- **Database Ready**: Data properly formatted for PostgreSQL storage 