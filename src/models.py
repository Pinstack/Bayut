from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Property(Base):
    __tablename__ = "properties"
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
    # Relationships
    locations = relationship(
        "Location", back_populates="property", cascade="all, delete-orphan"
    )
    media = relationship(
        "Media", back_populates="property", cascade="all, delete-orphan"
    )
    payment_plans = relationship(
        "PaymentPlan", back_populates="property", cascade="all, delete-orphan"
    )
    documents = relationship(
        "Document", back_populates="property", cascade="all, delete-orphan"
    )
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    level = Column(Integer, nullable=True)
    external_id = Column(String, nullable=True)
    name = Column(String, nullable=True)
    name_l1 = Column(String, nullable=True)
    slug = Column(String, nullable=True)
    slug_l1 = Column(String, nullable=True)
    property = relationship("Property", back_populates="locations")


class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    type = Column(String, nullable=False)  # photo, video, floorplan
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    property = relationship("Property", back_populates="media")


class Agency(Base):
    __tablename__ = "agencies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=True)
    logo = Column(String, nullable=True)
    properties = relationship("Property", backref="agency")


class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    properties = relationship("Property", backref="agent")


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    developer = Column(String, nullable=True)
    amenities = Column(JSONB, nullable=True)
    properties = relationship("Property", backref="project")


class PaymentPlan(Base):
    __tablename__ = "payment_plans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    plan_type = Column(String, nullable=True)
    down_payment = Column(Float, nullable=True)
    installments = Column(JSONB, nullable=True)
    property = relationship("Property", back_populates="payment_plans")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    doc_type = Column(String, nullable=True)
    url = Column(String, nullable=True)
    property = relationship("Property", back_populates="documents")


class UniqueLocation(Base):
    __tablename__ = "unique_locations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String, nullable=True)
    name = Column(String, nullable=True)
    name_l1 = Column(String, nullable=True)
    slug = Column(String, nullable=True)
    slug_l1 = Column(String, nullable=True)
    level = Column(Integer, nullable=True)
    parent_id = Column(Integer, ForeignKey("unique_locations.id"), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    parent = relationship("UniqueLocation", remote_side=[id], backref="children")
    # Unique constraint on (external_id, level) is handled by migration


class PropertyLocation(Base):
    __tablename__ = "property_locations"
    property_id = Column(Integer, ForeignKey("properties.id"), primary_key=True)
    location_id = Column(Integer, ForeignKey("unique_locations.id"), primary_key=True)
    hierarchy_level = Column(Integer, primary_key=True)
    property = relationship("Property", backref="property_locations")
    location = relationship("UniqueLocation", backref="property_locations")
