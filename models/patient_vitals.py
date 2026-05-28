from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from database import Base


class PatientVitalsModel(Base):
    __tablename__ = "patient_vitals"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    can_walk = Column(Boolean, nullable=False)
    breathing = Column(Boolean, nullable=False)
    airway_opened = Column(Boolean, nullable=False)
    resp_rate = Column(Integer, nullable=False)
    radial_pulse = Column(Boolean, nullable=False)
    cap_refill = Column(Float, nullable=False)
    follows_commands = Column(Boolean, nullable=False)

    patient = relationship("PatientModel", back_populates="vitals")
