from datetime import datetime

from models.audit_log import AuditLogModel
from models.patient import PatientModel
from sqlalchemy.orm import Session


WORKFLOW_STATUSES = {
    "NEW",
    "TRIAGED",
    "WAITING_DOCTOR",
    "IN_TREATMENT",
    "AWAITING_TRANSPORT",
    "TRANSFERRED",
    "DISCHARGED",
    "DECEASED",
}

ALLOWED_TRANSITIONS = {
    "NEW": {"TRIAGED"},
    "TRIAGED": {"WAITING_DOCTOR", "IN_TREATMENT"},
    "WAITING_DOCTOR": {"IN_TREATMENT", "AWAITING_TRANSPORT", "DISCHARGED"},
    "IN_TREATMENT": {"AWAITING_TRANSPORT", "TRANSFERRED", "DISCHARGED", "DECEASED"},
    "AWAITING_TRANSPORT": {"TRANSFERRED", "DISCHARGED"},
    "TRANSFERRED": {"IN_TREATMENT", "DISCHARGED"},
    "DISCHARGED": set(),
    "DECEASED": set(),
}


class WorkflowService:
    def validate_status(self, status: str) -> str:
        normalized = status.strip().upper()
        if normalized not in WORKFLOW_STATUSES:
            raise ValueError(f"Invalid workflow status: {normalized}")
        return normalized

    def transition_patient(self, db: Session, patient: PatientModel, target_status: str, message: str | None = None) -> PatientModel:
        target_status = self.validate_status(target_status)
        current_status = patient.status or "NEW"
        if current_status == target_status:
            return patient

        allowed = ALLOWED_TRANSITIONS.get(current_status, set())
        if target_status not in allowed:
            raise ValueError(
                f"Invalid transition from {current_status} to {target_status}. Allowed: {sorted(allowed)}"
            )

        patient.status = target_status
        audit_entry = AuditLogModel(
            patient_id=patient.id,
            event_type="STATE_TRANSITION",
            old_status=current_status,
            new_status=target_status,
            message=message or "Workflow transition",
            created_at=datetime.utcnow(),
        )

        db.add(patient)
        db.add(audit_entry)
        db.commit()
        db.refresh(patient)
        return patient
