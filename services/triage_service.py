from sqlalchemy.orm import Session

from models.patient import PatientModel
from models.patient_vitals import PatientVitalsModel
from schemas.patient_schema import Patient


class TriageService:
    def __init__(self):
        pass

    def save_patient(self, db: Session, incident_id: int, patient: Patient, triage_tag: str) -> PatientModel:
        db_patient = PatientModel(
            incident_id=incident_id,
            triage_tag=triage_tag,
            can_walk=patient.can_walk,
            breathing=patient.breathing,
            airway_opened=patient.airway_opened,
            resp_rate=patient.resp_rate,
            radial_pulse=patient.radial_pulse,
            cap_refill=patient.cap_refill,
            follows_commands=patient.follows_commands,
        )
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)

        db_vitals = PatientVitalsModel(
            patient_id=db_patient.id,
            can_walk=patient.can_walk,
            breathing=patient.breathing,
            airway_opened=patient.airway_opened,
            resp_rate=patient.resp_rate,
            radial_pulse=patient.radial_pulse,
            cap_refill=patient.cap_refill,
            follows_commands=patient.follows_commands,
        )
        db.add(db_vitals)
        db.commit()

        return db_patient
