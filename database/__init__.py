import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
    DATABASE_URL = f"mysql+pymysql://root:{MYSQL_PASSWORD}@127.0.0.1:3307/mci_triage"

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def migrate_database():
    inspector = inspect(engine)

    if "patients" not in inspector.get_table_names():
        Base.metadata.create_all(bind=engine)
        return

    patient_columns = {column["name"] for column in inspector.get_columns("patients")}

    with engine.begin() as connection:
        if "incident_id" not in patient_columns:
            connection.execute(text("ALTER TABLE patients ADD COLUMN incident_id INTEGER NOT NULL DEFAULT 0"))
            connection.execute(text("CREATE INDEX ix_patients_incident_id ON patients (incident_id)"))

        if "triage_tag" not in patient_columns:
            connection.execute(text("ALTER TABLE patients ADD COLUMN triage_tag VARCHAR(20) NOT NULL DEFAULT ''"))

        if "status" not in patient_columns:
            connection.execute(text("ALTER TABLE patients ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'TRIAGED'"))


migrate_database()
Base.metadata.create_all(bind=engine)
