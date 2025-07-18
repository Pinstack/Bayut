import os

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

from src.models import (
    Agency,
    Agent,
    Document,
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
    and populate the new normalized tables (media, agencies, agents, projects, payment_plans, documents).
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
                    agent_data = {
                        "name": agent_name,
                        "name_ar": agent_name_ar,
                        "phone": phone_info.get("number") if phone_info else None,
                        "email": extra_fields.get("email"),
                        "image": extra_fields.get("agent_image"),
                    }

            # Parse project
            project_data = None
            if extra_fields is not None and isinstance(extra_fields, dict):
                project_data = extra_fields.get("project")
                if not project_data and extra_fields.get("project_name"):
                    project_data = {
                        "name": extra_fields.get("project_name"),
                        "name_ar": extra_fields.get("project_name_ar"),
                        "description": extra_fields.get("project_description"),
                        "developer": extra_fields.get("developer"),
                    }

            # Upsert agency, agent, project
            agency_id = upsert_agency(session, agency_data)
            agent_id = upsert_agent(session, agent_data)
            project_id = upsert_project(session, project_data)

            # Update property with foreign keys
            if agency_id is not None:  # type: ignore
                prop.agency_id = agency_id  # type: ignore
            if agent_id is not None:  # type: ignore
                prop.agent_id = agent_id  # type: ignore
            if project_id is not None:  # type: ignore
                prop.project_id = project_id  # type: ignore

            # Parse and insert media
            media_list = extra_fields.get("media", []) if extra_fields else []
            for media_item in media_list:
                if isinstance(media_item, dict):
                    media_data = {
                        "property_id": prop.id,
                        "type": media_item.get("type", "image"),
                        "url": media_item.get("url"),
                        "title": media_item.get("title"),
                        "description": media_item.get("description"),
                    }
                    session.merge(Media(**media_data))

            # Parse and insert payment plans
            payment_plans = (
                extra_fields.get("payment_plans", []) if extra_fields else []
            )
            for plan in payment_plans:
                if isinstance(plan, dict):
                    plan_data = {
                        "property_id": prop.id,
                        "name": plan.get("name"),
                        "description": plan.get("description"),
                        "down_payment": plan.get("down_payment"),
                        "monthly_payment": plan.get("monthly_payment"),
                        "duration": plan.get("duration"),
                    }
                    session.merge(PaymentPlan(**plan_data))

            # Parse and insert documents
            documents = extra_fields.get("documents", []) if extra_fields else []
            for doc in documents:
                if isinstance(doc, dict):
                    doc_data = {
                        "property_id": prop.id,
                        "type": doc.get("type"),
                        "title": doc.get("title"),
                        "url": doc.get("url"),
                        "description": doc.get("description"),
                    }
                    session.merge(Document(**doc_data))

        session.commit()
        print(f"✅ Backfilled {len(properties)} properties to normalized tables")
    except Exception as e:
        session.rollback()
        print(f"❌ Error during backfill: {e}")
        raise
    finally:
        session.close()


def get_property_stats():
    """Get statistics about the properties in the database."""
    session = SessionLocal()
    try:
        total_properties = session.query(Property).count()
        properties_with_agency = (
            session.query(Property).filter(Property.agency_id.isnot(None)).count()
        )
        properties_with_agent = (
            session.query(Property).filter(Property.agent_id.isnot(None)).count()
        )
        properties_with_project = (
            session.query(Property).filter(Property.project_id.isnot(None)).count()
        )

        total_agencies = session.query(Agency).count()
        total_agents = session.query(Agent).count()
        total_projects = session.query(Project).count()
        total_media = session.query(Media).count()
        total_payment_plans = session.query(PaymentPlan).count()
        total_documents = session.query(Document).count()

        return {
            "properties": {
                "total": total_properties,
                "with_agency": properties_with_agency,
                "with_agent": properties_with_agent,
                "with_project": properties_with_project,
            },
            "related_data": {
                "agencies": total_agencies,
                "agents": total_agents,
                "projects": total_projects,
                "media": total_media,
                "payment_plans": total_payment_plans,
                "documents": total_documents,
            },
        }
    finally:
        session.close()
