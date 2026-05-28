from datetime import datetime

from pydantic import BaseModel, Field


class EventBase(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PatientTriagedEvent(EventBase):
    incident_id: int
    patient_id: int
    triage_tag: str
    status: str
    risk_level: str
    resources: list[str]


class VitalsUpdatedEvent(EventBase):
    incident_id: int
    patient_id: int
    timestamp: datetime
    resp_rate: int
    cap_refill: float
    follows_commands: bool
    status: str
