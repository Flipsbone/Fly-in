from pydantic import BaseModel, Field, field_validator, model_validator


class Drone_Approval(BaseModel):
    nb_drones: int = Field(ge=1)


class Zone_Approval(BaseModel):
    name: str
    x: int
    y: int
    metadata: str = ""

    @field_validator('name')
    @classmethod
    def name_must_not_contain_dash(cls, name: str) -> str:
        if '-' in name:
            raise ValueError("zone names cannot contain dashes")
        return name


class Connection_Approval(BaseModel):
    link_1: str
    link_2: str

    @model_validator(mode="after")
    def validate_link_rules(self) -> 'Connection_Approval':
        if self.link_1 == self.link_2:
            raise ValueError("link cannot connect to itself")
        if self.link_1 > self.link_2:
            self.link_1, self.link_2 = self.link_2, self.link_1
        return self
