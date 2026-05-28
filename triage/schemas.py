from pydantic import BaseModel


class Patient(BaseModel):
    can_walk: bool
    breathing: bool
    airway_opened: bool
    resp_rate: int
    radial_pulse: bool
    cap_refill: float
    follows_commands: bool
