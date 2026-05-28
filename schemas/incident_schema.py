from pydantic import BaseModel


class Incident(BaseModel):
    name: str
    location: str
