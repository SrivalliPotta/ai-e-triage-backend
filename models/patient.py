from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class PatientModel(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    triage_tag = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="NEW")
    can_walk = Column(Boolean, nullable=False)
    breathing = Column(Boolean, nullable=False)
    airway_opened = Column(Boolean, nullable=False)
    resp_rate = Column(Integer, nullable=False)
    radial_pulse = Column(Boolean, nullable=False)
    cap_refill = Column(Float, nullable=False)
    follows_commands = Column(Boolean, nullable=False)

    incident = relationship("IncidentModel", back_populates="patients")
    vitals = relationship("PatientVitalsModel", back_populates="patient", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLogModel", back_populates="patient", cascade="all, delete-orphan")
