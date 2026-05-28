from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.security import get_db, require_role
from models.patient import PatientModel
from models.user import UserModel
from schemas.patient_schema import Patient
from services.command_service import CommandService
from services.incident_service import IncidentService

router = APIRouter()


@router.post("/triage/{incident_id}")
async def triage(
    incident_id: int,
    patient: Patient,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(["Admin", "Medic"])),
):
    incident = IncidentService.get_incident_by_id(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    command_service = CommandService()
    db_patient = await command_service.triage_patient(db, incident_id, patient)
    return db_patient


@router.put("/patients/{patient_id}/status")
async def update_patient_status(
    patient_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(["Admin", "Medic"])),
):
    allowed_statuses = {
        "NEW",
        "TRIAGED",
        "WAITING_DOCTOR",
        "IN_TREATMENT",
        "AWAITING_TRANSPORT",
        "TRANSFERRED",
        "DISCHARGED",
        "DECEASED",
    }
    status_value = status.strip().upper()
    if status_value not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values: {', '.join(sorted(allowed_statuses))}",
        )

    db_patient = db.query(PatientModel).filter(PatientModel.id == patient_id).first()
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    db_patient.status = status_value
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient
