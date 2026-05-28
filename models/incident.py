from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    location = Column(String(120), nullable=False)

    patients = relationship("PatientModel", back_populates="incident")
