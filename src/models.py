from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Property(Base):
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    title_ar = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    location = Column(String, nullable=False)
    area = Column(Float, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    property_type = Column(String, nullable=True)
    purpose = Column(String, nullable=True)
    permit_number = Column(String, nullable=True)
    is_verified = Column(Boolean, nullable=True)
    extra_fields = Column(JSONB, nullable=True) 