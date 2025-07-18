from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from src.models import Property, Base
import os

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://raedmund@localhost:5432/bayut'
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Get valid Property model columns
PROPERTY_COLUMNS = {c.name for c in Property.__table__.columns}

def bulk_insert_properties(properties_data):
    """
    Insert or update a list of property dicts into the properties table.
    Uses upsert (ON CONFLICT DO UPDATE) on external_id.
    """
    session = SessionLocal()
    try:
        filtered = [
            {k: v for k, v in data.items() if k in PROPERTY_COLUMNS}
            for data in properties_data
        ]
        if not filtered:
            return
        stmt = insert(Property).values(filtered)
        update_cols = {c: getattr(stmt.excluded, c) for c in PROPERTY_COLUMNS if c != 'external_id'}
        stmt = stmt.on_conflict_do_update(
            index_elements=['external_id'],
            set_=update_cols
        )
        session.execute(stmt)
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close() 