from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.security import get_db, require_role
from models.user import UserModel
from schemas.incident_schema import Incident
from services.incident_service import IncidentService

router = APIRouter()


@router.post("/incidents")
def create_incident(
    incident: Incident,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(["Admin", "Commander"])),
):
    return IncidentService.create_incident(db, incident)


@router.get("/incidents")
def list_incidents(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(["Admin", "Commander", "Medic"])),
):
    return IncidentService.list_incidents(db)


@router.get("/incidents/{incident_id}/dashboard")
def incident_dashboard(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(["Admin", "Commander"])),
):
    dashboard = IncidentService.get_incident_dashboard(db, incident_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return dashboard
