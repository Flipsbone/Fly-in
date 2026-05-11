from pydantic import BaseModel, Field, field_validator, model_validator


class Drone_Approval(BaseModel):
    nb_drones: int = Field(ge=1)


class Zone_Approval(BaseModel):
    name: str
    x: int
    y: int
    zone: str = "normal"
    color: str | None = None
    max_drones: int = 1

    @field_validator('name')
    @classmethod
    def name_must_not_contain_dash(cls, name: str) -> str:
        if '-' in name:
            raise ValueError("zone names cannot contain dashes")
        return name

    @model_validator(mode="before")
    @classmethod
    def extract_metadata(cls, data: dict) -> dict:
        metadata_str = data.get("metadata", "")
        if not metadata_str:
            return data

        if not (metadata_str.startswith("[") and metadata_str.endswith("]")):
            raise ValueError("Metadata must be enclosed in []")

        metadata_str_clean = metadata_str.strip("[]")
        clean_metadata = metadata_str_clean.strip().split()
        zone_metadata: dict[str, str | int] = {}
        allowed_keys = ["color", "max_drones", "zone"]
        allowed_zone = ["priority", "restricted", "normal", "blocked"]
        for item in clean_metadata:
            if "=" not in item:
                raise ValueError("Metadata format must be key=value"
                                 "(e.g., [color=red])")
            key, value_str = item.split("=", 1)
            key = key.strip().lower()
            value_str = value_str.strip().lower()
            if key not in allowed_keys:
                raise ValueError(f"Unknown metadata key: '{key}'")
            if key in zone_metadata:
                raise ValueError(f"{key} cant be present twice")
            match key:
                case "color":
                    value_isalpha = value_str.isalpha()
                    if not value_isalpha:
                        raise ValueError(f"metadata value: '{value_str}' "
                                         "is not valid single-word strings"
                                         " (e.g., red, blue, gray).")
                    zone_metadata[key] = value_str
                case "zone":
                    if value_str not in allowed_zone:
                        raise ValueError("Unknown metadata value: "
                                         f"'{value_str}'")
                    zone_metadata[key] = value_str
                case "max_drones":
                    val_int = int(value_str)
                    if val_int < 1:
                        raise ValueError(f"metadata value: '{value_str}' "
                                         "must be >= 1")
                    zone_metadata[key] = val_int
        data.update(zone_metadata)
        data.pop("metadata", None)
        return data


class Connection_Approval(BaseModel):
    link_1: str
    link_2: str
    max_link_capacity: int = 1

    @model_validator(mode="before")
    @classmethod
    def extract_metadata(cls, data: dict) -> dict:
        metadata_str = data.get("metadata", "")
        if not metadata_str:
            return data

        if not (metadata_str.startswith("[") and metadata_str.endswith("]")):
            raise ValueError("Metadata must be enclosed in []")

        clean_meta = metadata_str.strip("[]")
        if "=" not in clean_meta:
            raise ValueError("Metadata format must be key=value"
                             "(e.g., [max_link_capacity=1])")

        key, value_str = clean_meta.split("=", 1)
        key = key.strip()
        value_str = value_str.strip()

        if key != "max_link_capacity":
            raise ValueError(f"Unknown metadata key: '{key}'")
        try:
            value = int(value_str)
            if value < 1:
                raise ValueError
            data["max_link_capacity"] = value
        except (ValueError):
            raise ValueError("max_link_capacity must be an integer >= 1")
        return data

    @model_validator(mode="after")
    def validate_link_rules(self) -> 'Connection_Approval':
        if self.link_1 == self.link_2:
            raise ValueError("link cannot connect to itself")
        if self.link_1 > self.link_2:
            self.link_1, self.link_2 = self.link_2, self.link_1
        return self
