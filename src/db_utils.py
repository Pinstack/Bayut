import os

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

from models import (
    Agency,
    Agent,
    Document,
    Location,
    Media,
    PaymentPlan,
    Project,
    Property,
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://raedmund@localhost:5432/bayut")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

PROPERTY_COLUMNS = {c.name for c in Property.__table__.columns}


# --- New Hybrid Ingestion Logic ---
def upsert_agency(session, agency_data):
    if not agency_data or not agency_data.get("name"):
        return None
    stmt = insert(Agency).values(**agency_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["name"],
        set_={k: getattr(stmt.excluded, k) for k in agency_data if k != "name"},
    )
    session.execute(stmt)
    session.flush()
    agency = session.query(Agency).filter_by(name=agency_data["name"]).first()
    return agency.id if agency else None


def upsert_agent(session, agent_data):
    if not agent_data or not agent_data.get("name"):
        return None
    stmt = insert(Agent).values(**agent_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["name"],
        set_={k: getattr(stmt.excluded, k) for k in agent_data if k != "name"},
    )
    session.execute(stmt)
    session.flush()
    agent = session.query(Agent).filter_by(name=agent_data["name"]).first()
    return agent.id if agent else None


def upsert_project(session, project_data):
    if not project_data or not project_data.get("name"):
        return None
    stmt = insert(Project).values(**project_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["name"],
        set_={k: getattr(stmt.excluded, k) for k in project_data if k != "name"},
    )
    session.execute(stmt)
    session.flush()
    project = session.query(Project).filter_by(name=project_data["name"]).first()
    return project.id if project else None


def insert_full_property_record(property_data):
    """
    Insert a property and all related normalized data in a single transaction.
    property_data: dict with keys for property, agency, agent, project, locations, media, payment_plans, documents
    """
    session = SessionLocal()
    try:
        # Upsert agency, agent, project
        agency_id = upsert_agency(session, property_data.get("agency"))
        agent_id = upsert_agent(session, property_data.get("agent"))
        project_id = upsert_project(session, property_data.get("project"))
        # Prepare property core fields
        prop_fields = {k: v for k, v in property_data.items() if k in PROPERTY_COLUMNS}
        prop_fields["agency_id"] = agency_id
        prop_fields["agent_id"] = agent_id
        prop_fields["project_id"] = project_id
        # Upsert property
        stmt = insert(Property).values(**prop_fields)
        update_cols = {
            c: getattr(stmt.excluded, c) for c in PROPERTY_COLUMNS if c != "external_id"
        }
        update_cols.update(
            {"agency_id": agency_id, "agent_id": agent_id, "project_id": project_id}
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["external_id"], set_=update_cols
        )
        session.execute(stmt)
        session.flush()
        prop = (
            session.query(Property)
            .filter_by(external_id=prop_fields["external_id"])
            .first()
        )
        if prop is None:
            raise ValueError(
                f"Property with external_id {prop_fields['external_id']} not found after insertion"
            )
        property_id = prop.id
        # Insert related locations
        for loc in property_data.get("locations", []):
            loc["property_id"] = property_id
            session.merge(Location(**loc))
        # Insert related media
        for media in property_data.get("media", []):
            media["property_id"] = property_id
            session.merge(Media(**media))
        # Insert related payment plans
        for plan in property_data.get("payment_plans", []):
            plan["property_id"] = property_id
            session.merge(PaymentPlan(**plan))
        # Insert related documents
        for doc in property_data.get("documents", []):
            doc["property_id"] = property_id
            session.merge(Document(**doc))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# --- Retain old bulk insert for reference ---
def bulk_insert_properties(properties_data):
    session = SessionLocal()
    try:
        filtered = [
            {k: v for k, v in data.items() if k in PROPERTY_COLUMNS}
            for data in properties_data
        ]
        if not filtered:
            return
        stmt = insert(Property).values(filtered)
        update_cols = {
            c: getattr(stmt.excluded, c) for c in PROPERTY_COLUMNS if c != "external_id"
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=["external_id"], set_=update_cols
        )
        session.execute(stmt)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def backfill_properties_to_normalized_tables():
    """
    For each property in the DB, parse extra_fields and related columns,
    and populate the new normalized tables (locations, media, agencies, agents, projects, payment_plans, documents).
    """
    session = SessionLocal()
    try:
        properties = session.query(Property).all()
        for prop in properties:
            # Parse agency - check both nested object and flat fields
            agency_data = None
            extra_fields = prop.extra_fields
            if extra_fields is not None and isinstance(extra_fields, dict):
                # First try nested agency object
                agency_data = extra_fields.get("agency")
                # If not found, try flat agency_name field
                if not agency_data and extra_fields.get("agency_name"):
                    agency_name_obj = extra_fields.get("agency_name")
                    if isinstance(agency_name_obj, dict):
                        agency_data = {
                            "name": agency_name_obj.get("name"),
                            "name_ar": agency_name_obj.get("name_l1"),
                            "logo": (
                                agency_name_obj.get("logo", {}).get("url")
                                if agency_name_obj.get("logo")
                                else None
                            ),
                        }
                    elif isinstance(agency_name_obj, str):
                        agency_data = {"name": agency_name_obj}

            # Parse agent - check both nested object and flat fields
            agent_data = None
            if extra_fields is not None and isinstance(extra_fields, dict):
                # First try nested agent object
                agent_data = extra_fields.get("agent")
                # If not found, try flat agent_name field
                if not agent_data and extra_fields.get("agent_name"):
                    agent_name = extra_fields.get("agent_name")
                    agent_name_ar = extra_fields.get("agent_name_ar")
                    phone_info = extra_fields.get("phone", {})
                    if isinstance(phone_info, dict):
                        phone = phone_info.get("mobile")
                        whatsapp = phone_info.get("whatsapp")
                    else:
                        phone = None
                        whatsapp = None

                    agent_data = {
                        "name": agent_name,
                        "name_ar": agent_name_ar,
                        "phone": phone,
                        "whatsapp": whatsapp,
                    }

            # Parse project
            project_data = None
            if extra_fields is not None and isinstance(extra_fields, dict):
                project_data = extra_fields.get("project")

            # Upsert agency, agent, project
            agency_id = upsert_agency(session, agency_data)
            agent_id = upsert_agent(session, agent_data)
            project_id = upsert_project(session, project_data)

            # Update property with FKs (handle None values)
            if agency_id is not None:
                prop.agency_id = agency_id
            if agent_id is not None:
                prop.agent_id = agent_id
            if project_id is not None:
                prop.project_id = project_id
            session.flush()
            property_id = prop.id

            # Locations
            locations = []
            if extra_fields is not None and isinstance(extra_fields, dict):
                locs = extra_fields.get("location_hierarchy") or extra_fields.get(
                    "location"
                )
                if isinstance(locs, list):
                    for location in locs:
                        locations.append(
                            {
                                "property_id": property_id,
                                "level": location.get("level"),
                                "external_id": location.get("externalID"),
                                "name": location.get("name"),
                                "name_l1": location.get("name_l1"),
                                "slug": location.get("slug"),
                                "slug_l1": location.get("slug_l1"),
                            }
                        )
            for loc in locations:
                session.merge(Location(**loc))

            # Media - handle photoIDs, photo_url, and photos
            media_items = []
            if extra_fields is not None and isinstance(extra_fields, dict):
                # Handle photoIDs (array of IDs)
                photo_ids = extra_fields.get("photoIDs", [])
                if isinstance(photo_ids, list):
                    for photo_id in photo_ids:
                        # Construct URL from photo ID (Bayut pattern)
                        photo_url = f"https://bayut-sa-production.s3.eu-central-1.amazonaws.com/image/{photo_id}"
                        media_items.append(
                            {
                                "property_id": property_id,
                                "type": "photo",
                                "url": photo_url,
                                "title": f"Photo {photo_id}",
                            }
                        )

                # Handle photo_url object
                photo_url_obj = extra_fields.get("photo_url")
                if isinstance(photo_url_obj, dict) and photo_url_obj.get("url"):
                    media_items.append(
                        {
                            "property_id": property_id,
                            "type": "photo",
                            "url": photo_url_obj.get("url"),
                            "title": photo_url_obj.get("title") or "Cover Photo",
                        }
                    )

                # Handle photos array (if exists)
                photos = extra_fields.get("photos") or []
                for p in photos:
                    if isinstance(p, dict) and p.get("url"):
                        media_items.append(
                            {
                                "property_id": property_id,
                                "type": "photo",
                                "url": p.get("url"),
                                "title": p.get("title"),
                            }
                        )

                # Handle videos array (if exists)
                videos = extra_fields.get("videos") or []
                for v in videos:
                    if isinstance(v, dict) and v.get("url"):
                        media_items.append(
                            {
                                "property_id": property_id,
                                "type": "video",
                                "url": v.get("url"),
                                "title": v.get("title"),
                            }
                        )

            # Insert media items (avoid duplicates)
            for media in media_items:
                if media["url"]:
                    # Check if this URL already exists for this property
                    existing = (
                        session.query(Media)
                        .filter_by(property_id=property_id, url=media["url"])
                        .first()
                    )
                    if not existing:
                        session.merge(Media(**media))

            # Payment plans
            payment_plans = []
            if extra_fields is not None and isinstance(extra_fields, dict):
                plans = (
                    extra_fields.get("paymentPlans")
                    or extra_fields.get("payment_plans")
                    or []
                )
                for plan in plans:
                    payment_plans.append(
                        {
                            "property_id": property_id,
                            "plan_type": plan.get("plan_type"),
                            "down_payment": plan.get("down_payment"),
                            "installments": plan.get("installments"),
                        }
                    )
            for plan in payment_plans:
                session.merge(PaymentPlan(**plan))

            # Documents
            documents = []
            if extra_fields is not None and isinstance(extra_fields, dict):
                docs = extra_fields.get("documents") or []
                for doc in docs:
                    documents.append(
                        {
                            "property_id": property_id,
                            "doc_type": doc.get("doc_type"),
                            "url": doc.get("url"),
                        }
                    )
            for doc in documents:
                if doc["url"]:
                    session.merge(Document(**doc))

        session.commit()
        print(
            f"Successfully backfilled normalized tables for {len(properties)} properties"
        )
    except Exception as e:
        session.rollback()
        print(f"Error during backfill: {e}")
        raise
    finally:
        session.close()
