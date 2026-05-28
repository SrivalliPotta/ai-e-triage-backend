from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import auth_router, incident_router, triage_router, websocket_router
from core import create_default_user
from database import Base, engine, SessionLocal
from models.patient import PatientModel
from models.incident import IncidentModel
from models.user import UserModel
from models.patient_vitals import PatientVitalsModel
from models.audit_log import AuditLogModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
create_default_user()

app.include_router(auth_router)
app.include_router(incident_router)
app.include_router(triage_router)
app.include_router(websocket_router)


@app.get("/")
def root():
    return {"message": "MCI TRIAGE BACKEND"}


# Expose commonly used test helpers
SessionLocal = SessionLocal
PatientModel = PatientModel
IncidentModel = IncidentModel
UserModel = UserModel
