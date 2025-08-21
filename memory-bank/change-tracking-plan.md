# Change Tracking Implementation Plan

## Overview

This document outlines the comprehensive implementation plan for adding change tracking capabilities to the Bayut.sa Property Scraper. The system will track property listing changes over time, including price changes, new listings, updates, and removals, using location-based analysis.

## Architecture Summary

### Location-Based Approach
- **Primary**: Location-based tracking using Bayut's natural market boundaries
- **Temporal**: Daily tracking with configurable granularity
- **Automated**: Background scheduling with change detection and notifications

### Key Components
1. **Enhanced Database Schema**: Price history and change tracking tables
2. **Change Detection Engine**: State management and comparison algorithms
3. **Location Analysis**: Location-based market analysis
4. **Notification System**: Alerts for significant changes
5. **Scheduling System**: Automated background tasks

## Phase 1: Database Schema Enhancement (Week 1)

### 1.1 Create New Tables

#### Price History Table
```sql
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(255) NOT NULL,
    location_id INTEGER REFERENCES locations(id),
    asking_price DECIMAL(15,2) NOT NULL,
    price_per_sqm DECIMAL(15,2),
    currency VARCHAR(10) DEFAULT 'SAR',
    property_type VARCHAR(100),
    purpose VARCHAR(50),
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    listing_date TIMESTAMP,
    
    INDEX idx_property_date (property_id, captured_at),
    INDEX idx_location_date (location_id, captured_at)
);
```

#### Property Changes Table
```sql
CREATE TABLE property_changes (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    property_id VARCHAR(255) NOT NULL,
    location_id INTEGER REFERENCES locations(id),
    old_data JSONB,
    new_data JSONB,
    change_percentage DECIMAL(5,2),
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_property_event (property_id, event_timestamp),
    INDEX idx_location_event (location_id, event_timestamp),
    INDEX idx_event_type (event_type, event_timestamp)
);
```

#### Scraping States Table
```sql
CREATE TABLE scraping_states (
    id SERIAL PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    state_data JSONB NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(location),
    INDEX idx_location_updated (location, last_updated)
);
```

### 1.2 Update Models
- Add SQLAlchemy models for new tables
- Create Alembic migrations
- Update existing models to support change tracking

### 1.3 Database Utilities
- Add functions for bulk price history insertion
- Add change event recording functions
- Add state management functions

## Phase 2: Enhanced Scraper with Change Detection (Week 2)

### 2.1 State Management System
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

### 2.2 Change Detection Engine
```python
class ChangeDetector:
    def __init__(self, db_session):
        self.session = db_session
        self.state_manager = StateManager(db_session)
    
    async def detect_changes(self, location: str, current_data: List[Dict]) -> List[ChangeEvent]:
        """Detect changes between previous and current state"""
        previous_state = await self.state_manager.get_previous_state(location)
        changes = self._compare_states(previous_state, current_data)
        
        # Record changes in database
        await self._record_changes(changes)
        
        # Update state
        await self.state_manager.update_state(location, current_data)
        
        return changes
```

### 2.3 Enhanced Scraper Integration
```python
class ChangeTrackingScraper(EnhancedBayutScraper):
    def __init__(self, db_session):
        super().__init__()
        self.change_detector = ChangeDetector(db_session)
        self.price_history_tracker = PriceHistoryTracker(db_session)
    
    async def scrape_with_change_detection(self, location: str, max_pages: int = 10):
        """Scrape properties and detect changes"""
        # Scrape current data
        listings = await self.scrape_by_location(location, max_pages)
        
        # Detect changes
        changes = await self.change_detector.detect_changes(location, listings)
        
        # Record price history
        await self.price_history_tracker.record_prices(location, listings)
        
        return {
            'listings': listings,
            'changes': changes
        }
```

## Phase 3: Location-Based Analysis (Week 3)

### 3.1 Location Analysis Functions
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

### 3.2 Enhanced Data Models
```python
@dataclass
class LocationInsight:
    location: str
    avg_price: float
    price_trend: float  # percentage change
    listing_count: int
    price_per_sqm: float
    analysis_date: datetime

@dataclass
class CrossLocationComparison:
    location1: str
    location2: str
    price_difference: float
    price_ratio: float
    market_correlation: float
```

## Phase 4: Notification System and Scheduling (Week 4)

### 4.1 Notification Configuration
```python
class NotificationConfig:
    def __init__(self):
        self.thresholds = {
            'price_change': 5.0,  # 5% price change
            'new_listings': 10,   # 10 new listings
            'removed_listings': 5  # 5 removed listings
        }
        self.channels = ['email', 'webhook']
        self.frequency_control = {
            'max_notifications_per_hour': 10,
            'cooldown_minutes': 30
        }
```

### 4.2 Notification Channels
```python
class NotificationSystem:
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.email_sender = EmailSender()
        self.webhook_sender = WebhookSender()
    
    async def process_changes(self, changes: List[ChangeEvent]):
        """Process changes and send notifications"""
        for change in changes:
            if self._should_notify(change):
                await self._send_notification(change)
    
    async def _send_email(self, change: ChangeEvent):
        """Send email notification"""
        subject = f"Property Change Alert: {change.event_type}"
        body = self._format_email_body(change)
        await self.email_sender.send(subject, body)
    
    async def _send_webhook(self, change: ChangeEvent):
        """Send webhook notification"""
        payload = self._format_webhook_payload(change)
        await self.webhook_sender.send(payload)
```

### 4.3 Automated Scheduling
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

class ChangeTrackingScheduler:
    def __init__(self, db_url: str):
        self.scheduler = AsyncIOScheduler(
            jobstores={
                'default': SQLAlchemyJobStore(url=db_url)
            },
            timezone='Asia/Riyadh'
        )
        self.scraper = ChangeTrackingScraper(db_session)
    
    def setup_jobs(self):
        """Setup scheduled jobs"""
        # Daily scraping for major locations
        self.scheduler.add_job(
            self._scrape_major_locations,
            'cron',
            hour=6,  # 6 AM Riyadh time
            id='daily_major_locations'
        )
        
        # Hourly scraping for high-value areas
        self.scheduler.add_job(
            self._scrape_high_value_areas,
            'interval',
            hours=1,
            id='hourly_high_value'
        )
    
    async def _scrape_major_locations(self):
        """Scrape major locations daily"""
        major_locations = ['الرياض', 'جدة', 'الدمام', 'مكة', 'المدينة']
        for location in major_locations:
            try:
                result = await self.scraper.scrape_with_change_detection(location)
                logging.info(f"Completed daily scraping for {location}")
            except Exception as e:
                logging.error(f"Failed to scrape {location}: {e}")
```

## Implementation Timeline

### Week 1: Database Schema
- [ ] Create new tables (price_history, property_changes, scraping_states)
- [ ] Update SQLAlchemy models
- [ ] Create Alembic migrations
- [ ] Test database operations

### Week 2: Change Detection
- [ ] Implement StateManager
- [ ] Implement ChangeDetector
- [ ] Integrate with existing scraper
- [ ] Test change detection logic

### Week 3: Location Analysis
- [ ] Implement LocationAnalyzer
- [ ] Add location-based analysis functions
- [ ] Create market insights and reporting
- [ ] Test location analysis

### Week 4: Notifications and Scheduling
- [ ] Implement NotificationSystem
- [ ] Add email and webhook channels
- [ ] Configure automated scheduling
- [ ] Test complete system

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock external dependencies
- Test edge cases and error conditions

### Integration Tests
- Test component interactions
- Test database operations
- Test end-to-end workflows

### Performance Tests
- Test with large datasets
- Measure change detection performance
- Test location analysis efficiency

### End-to-End Tests
- Test complete change tracking workflow
- Test notification delivery
- Test scheduled operations

## Configuration Management

### Environment Variables
```bash
# Change tracking configuration
CHANGE_TRACKING_ENABLED=true
PRICE_CHANGE_THRESHOLD=5.0
POLLING_INTERVAL=3600

# Database configuration
DATABASE_URL=postgresql://user:password@localhost/bayut_db

# Notification configuration
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
WEBHOOK_URL=https://your-webhook-endpoint.com
```

### Configuration Files
```python
# config/change_tracking.py
CHANGE_TRACKING_CONFIG = {
    'enabled': True,
    'polling_interval': 3600,
    'price_change_threshold': 5.0,
    'locations': ['الرياض', 'جدة', 'الدمام'],
    'notification_channels': ['email', 'webhook']
}
```

## Monitoring and Maintenance

### Performance Monitoring
- Track scraping performance metrics
- Monitor change detection accuracy
- Measure notification delivery success
- Monitor database performance

### Error Handling
- Implement comprehensive error logging
- Add retry mechanisms for failed operations
- Monitor for data quality issues
- Alert on system failures

### Data Management
- Implement data retention policies
- Archive old historical data
- Monitor database growth
- Optimize query performance

## Success Criteria

### Functional Requirements
- [ ] Track price changes for major locations
- [ ] Detect new, updated, and removed listings
- [ ] Provide location-based price analysis
- [ ] Generate alerts for significant changes
- [ ] Support automated daily scraping

### Performance Requirements
- [ ] Change detection completes within 5 minutes
- [ ] Location analysis handles 1000+ properties efficiently
- [ ] Notifications delivered within 1 minute
- [ ] Database queries optimized for large datasets

### Quality Requirements
- [ ] 99% accuracy in change detection
- [ ] Comprehensive error handling and logging
- [ ] Well-documented code and APIs
- [ ] Comprehensive test coverage

## Risk Mitigation

### Technical Risks
- **API Rate Limiting**: Implement robust rate limiting and backoff strategies
- **Data Quality Issues**: Add validation and filtering for problematic data
- **Performance Degradation**: Monitor and optimize database queries
- **System Failures**: Implement comprehensive error handling and recovery

### Operational Risks
- **Resource Constraints**: Monitor system resources and scale as needed
- **Data Loss**: Implement backup and recovery procedures
- **Security Issues**: Secure API keys and sensitive data
- **Maintenance Overhead**: Automate routine tasks and monitoring

## Future Enhancements

### Advanced Analytics
- Machine learning for price prediction
- Market trend analysis and forecasting
- Anomaly detection in price changes
- Competitive analysis features

### Enhanced Notifications
- Mobile push notifications
- SMS alerts for critical changes
- Customizable alert preferences
- Advanced filtering options

### Integration Capabilities
- REST API for external integrations
- Webhook support for real-time updates
- Data export in multiple formats
- Third-party system integrations

### Scalability Improvements
- Distributed processing for large datasets
- Caching layer for improved performance
- Microservices architecture
- Cloud deployment options 