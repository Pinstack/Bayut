# Agent-Agency Relationship Design

## Overview

The Bayut Property Scraper database supports a flexible agent-agency relationship that accommodates both agency-affiliated agents and independent agents.

## Database Schema

### Agent Table
```sql
agents:
  id (PK)
  name (NOT NULL, UNIQUE)
  name_ar
  phone
  whatsapp
  agency_id (FK -> agencies.id, NULLABLE)  -- Optional relationship
```

### Agency Table
```sql
agencies:
  id (PK)
  name (NOT NULL, UNIQUE)
  name_ar
  logo
```

### Property Table
```sql
properties:
  id (PK)
  -- ... other fields ...
  agency_id (FK -> agencies.id, NULLABLE)  -- Property's agency
  agent_id (FK -> agents.id, NULLABLE)     -- Property's agent
```

## Relationship Types

### 1. Agency-Affiliated Agents
- **Scenario**: Agent works for a specific real estate agency
- **Data**: `agent.agency_id` contains the agency's ID
- **Example**: "Ahmed Ali" works for "Al Rajhi Real Estate"

```python
agent = Agent(
    name="Ahmed Ali",
    agency_id=agency.id  # Linked to specific agency
)
```

### 2. Independent Agents
- **Scenario**: Agent works independently without agency affiliation
- **Data**: `agent.agency_id` is NULL
- **Example**: "Sarah Mohammed" is a freelance real estate agent

```python
agent = Agent(
    name="Sarah Mohammed",
    agency_id=None  # Independent agent
)
```

## Business Logic

### Property Listings
Properties can have:
1. **Both agency and agent**: Property listed by an agency with a specific agent
2. **Agency only**: Property listed by agency without specific agent
3. **Agent only**: Property listed by independent agent
4. **Neither**: Direct property listing (rare but possible)

### Data Integrity Rules
- If `property.agent_id` is set and `property.agent.agency_id` is set:
  - The agent should ideally belong to the same agency as the property
  - However, this is not enforced at the database level to allow flexibility
- Agents can exist without agencies (independent agents)
- Agencies can exist without agents (agency-only listings)

## Query Examples

### Find All Independent Agents
```python
independent_agents = session.query(Agent).filter(Agent.agency_id.is_(None)).all()
```

### Find All Agents for a Specific Agency
```python
agency_agents = session.query(Agent).filter(Agent.agency_id == agency_id).all()
```

### Find Properties by Independent Agent
```python
independent_agent_properties = session.query(Property).join(Agent).filter(
    Property.agent_id.isnot(None),
    Agent.agency_id.is_(None)
).all()
```

### Find Properties with Mismatched Agency/Agent
```python
mismatched_properties = session.query(Property).join(Agent).filter(
    Property.agency_id.isnot(None),
    Property.agent_id.isnot(None),
    Property.agency_id != Agent.agency_id
).all()
```

## Migration Considerations

### Existing Data
- All existing agents currently have `agency_id = NULL`
- This is correct for independent agents
- For agency-affiliated agents, the relationship can be established based on:
  - Property listings where agent and agency are both present
  - Manual data cleanup and assignment

### Data Population Strategy
1. **Automatic Matching**: Match agents to agencies based on property listings
2. **Manual Assignment**: Create admin interface for manual agent-agency assignments
3. **Scraper Enhancement**: Update scraper to capture agent-agency relationships from source data

## Benefits of This Design

### Flexibility
- Supports both traditional agency model and modern independent agent model
- Allows for gradual migration from independent to agency-affiliated agents
- Accommodates various business models in the real estate industry

### Data Integrity
- Maintains referential integrity through foreign keys
- Allows for optional relationships without data loss
- Supports future validation rules if needed

### Query Performance
- Efficient queries for both agency and independent agent scenarios
- Indexes on foreign keys for fast lookups
- Supports complex filtering and reporting

## Future Enhancements

### Validation Rules
```python
# Optional: Add validation to ensure agent belongs to property's agency
def validate_agent_agency_consistency(property):
    if property.agent and property.agency and property.agent.agency_id:
        if property.agent.agency_id != property.agency_id:
            # Log warning or raise validation error
            pass
```

### Agency Management
- Agency profile management
- Agent onboarding workflows
- Agency performance analytics

### Independent Agent Features
- Independent agent profiles
- Commission tracking for independent agents
- Direct client communication tools

## Conclusion

This design provides maximum flexibility while maintaining data integrity and supporting both traditional and modern real estate business models. The optional nature of the agent-agency relationship allows for gradual adoption and supports various market scenarios. 