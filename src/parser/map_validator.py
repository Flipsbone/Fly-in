from pydantic import BaseModel, Field


class Drone_Approval(BaseModel):
    nb_drones: int = Field(ge=1)


class Zone_Approval(BaseModel):
    name: str
    x: int
    y: int
    metadata: str = ""
