from sqlalchemy import JSON, Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True)
    external_id = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    title_ar = Column(String)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    location = Column(String, nullable=False)  # Simple location string
    location_id = Column(
        Integer, ForeignKey("locations.id")
    )  # Optional canonical location reference
    area = Column(Float)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    property_type = Column(String)
    purpose = Column(String)
    permit_number = Column(String)
    is_verified = Column(Boolean)
    extra_fields = Column(JSON)

    # Foreign keys to other tables
    agency_id = Column(Integer, ForeignKey("agencies.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))

    # Relationships
    agency = relationship("Agency", back_populates="properties")
    agent = relationship("Agent", back_populates="properties")
    project = relationship("Project", back_populates="properties")
    location_ref = relationship("Location", back_populates="properties")
    media = relationship("Media", back_populates="property")
    payment_plans = relationship("PaymentPlan", back_populates="property")
    documents = relationship("Document", back_populates="property")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    external_id = Column(String)
    name = Column(String, nullable=False, unique=True)
    name_ar = Column(String)
    slug = Column(String)
    level = Column(Integer, nullable=False)  # 1=city, 2=district, 3=neighborhood
    parent_id = Column(Integer, ForeignKey("locations.id"))
    latitude = Column(Float)
    longitude = Column(Float)

    # Self-referencing relationship for hierarchy
    parent = relationship("Location", remote_side=[id], back_populates="children")
    children = relationship("Location", back_populates="parent")

    # Properties in this location
    properties = relationship("Property", back_populates="location_ref")


class Agency(Base):
    __tablename__ = "agencies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    name_ar = Column(String)
    logo = Column(String)

    # Relationships
    properties = relationship("Property", back_populates="agency")
    agents = relationship("Agent", back_populates="agency")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    name_ar = Column(String)
    phone = Column(String)
    whatsapp = Column(String)
    agency_id = Column(
        Integer, ForeignKey("agencies.id")
    )  # Optional: Agent may work for an agency or be independent

    # Relationships
    agency = relationship("Agency", back_populates="agents")
    properties = relationship("Property", back_populates="agent")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    developer = Column(String)
    amenities = Column(JSON)

    # Relationships
    properties = relationship("Property", back_populates="project")


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    type = Column(String, nullable=False)  # image, video, floor_plan, etc.
    url = Column(String, nullable=False)
    title = Column(String)

    # Relationships
    property = relationship("Property", back_populates="media")


class PaymentPlan(Base):
    __tablename__ = "payment_plans"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    plan_type = Column(String)
    down_payment = Column(Float)
    installments = Column(JSON)

    # Relationships
    property = relationship("Property", back_populates="payment_plans")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    doc_type = Column(String)  # permit, contract, etc.
    url = Column(String)

    # Relationships
    property = relationship("Property", back_populates="documents")
