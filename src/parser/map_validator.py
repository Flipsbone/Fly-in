from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Any


class Drone_Approval(BaseModel):
    """Validation model for the drone count."""
    nb_drones: int = Field(ge=1)


class Zone_Approval(BaseModel):
    """Validation and normalization for zone (hub) lines.

    The model supports extracting optional metadata such as color,
    zone type and `max_drones` from a bracketed [..] string.
    """
    name: str
    x: int
    y: int
    zone: str = "normal"
    color: str | None = None
    max_drones: int = 1
    line: int

    @classmethod
    def _check_bracket(cls, metadata_str: str) -> bool:
        seen: dict[str, str] = {
            "]": "[",
        }
        stack = []
        count: int = 0
        for letter in metadata_str:
            if letter in "[":
                stack.append(letter)
                count += 1
            elif letter in seen:
                if not stack or stack.pop() != seen[letter] or count > 1:
                    return False
        return True

    @field_validator('name')
    @classmethod
    def name_must_not_contain_dash(cls, name: str) -> str:
        if '-' in name:
            raise ValueError("zone names cannot contain dashes")
        return name

    @model_validator(mode="before")
    @classmethod
    def extract_metadata(cls, data: dict[str, Any]) -> dict[str, Any]:
        metadata_str: str = data.get("metadata", "")
        if not metadata_str:
            return data
        if not (metadata_str.startswith("[") and metadata_str.endswith("]")):
            raise ValueError("Metadata must be enclosed in []")

        if not cls._check_bracket(metadata_str):
            raise ValueError("Metada must be enclosed with exactly by one []")

        metadata_content: str = metadata_str.strip("[]")
        metadata_items: list[str] = metadata_content.strip().split()
        zone_metadata: dict[str, str | int] = {}

        allowed_keys: set[str] = {
            "color", "max_drones", "zone"}
        allowed_zone: set[str] = {
            "priority", "restricted", "normal", "blocked"}

        for item in metadata_items:
            if "=" not in item:
                raise ValueError("Metadata format must be key=value"
                                 "(e.g., [color=red])")

            key, value_str = item.split("=", 1)
            key = key.lower()
            value_str = value_str.lower()

            if key not in allowed_keys:
                raise ValueError(f"Unknown metadata key: '{key}'")

            if key in zone_metadata:
                raise ValueError(f"{key} cant be present twice")

            match key:
                case "color":
                    value_isalpha: bool = value_str.isalpha()
                    if not value_isalpha:
                        raise ValueError(f"metadata value after '=' is "
                                         f" '{value_str} ' the format must"
                                         " be 'color=green' and the color"
                                         " must be single-word strings"
                                         " (e.g., red, blue, gray).")

                    zone_metadata[key] = value_str

                case "zone":
                    if value_str not in allowed_zone:
                        raise ValueError("Unknown metadata value: "
                                         f"'{value_str}'")

                    zone_metadata[key] = value_str

                case "max_drones":
                    try:
                        val_int: int = int(value_str)
                    except ValueError:
                        raise ValueError(f"max_drone value '{value_str}' "
                                         "must be an integer")
                    if val_int < 1:
                        raise ValueError(f"metadata value: '{value_str}' "
                                         "must be >= 1")

                    zone_metadata[key] = val_int

        data.update(zone_metadata)
        data.pop("metadata", None)
        return data


class Connection_Approval(BaseModel):
    """Validation for a connection line and optional metadata."""
    link_1: str
    link_2: str
    max_link_capacity: int = 1

    @model_validator(mode="before")
    @classmethod
    def extract_metadata(cls, data: dict[str, Any]) -> dict[str, int]:
        metadata_str: str = data.get("metadata", "")
        if not metadata_str:
            return data

        if not (metadata_str.startswith("[") and metadata_str.endswith("]")):
            raise ValueError("Metadata must be enclosed in [] "
                             "that means the data not respect "
                             "the folowing statement e.g., "
                             "[max_link_capacity=2]")

        metadata_content: str = metadata_str.strip("[]")
        if "=" not in metadata_content:
            raise ValueError("Metadata format must be key=value"
                             "(e.g., [max_link_capacity=1])")

        key, value_str = metadata_content.split("=", 1)
        key = key.strip().lower()
        max_drone_value_str = value_str.strip()

        if key != "max_link_capacity":
            raise ValueError(f"Unknown metadata key: '{key}'\n"
                             "Must be only e.g., [max_link_capacity=2]")
        try:
            max_drone_value = int(max_drone_value_str)
        except ValueError:
            raise ValueError("max_link_capacity must be an integer")
        if max_drone_value < 1:
            raise ValueError("max_link_capacity must be an integer >= 1")
        data["max_link_capacity"] = max_drone_value

        return data

    @model_validator(mode="after")
    def validate_link_rules(self) -> 'Connection_Approval':
        """Validate and normalize link order.

        Ensures a connection does not link to itself and orders link
        names so the tuple key is consistent.
        """
        if self.link_1 == self.link_2:
            raise ValueError("link cannot connect to itself")
        if self.link_1 > self.link_2:
            self.link_1, self.link_2 = self.link_2, self.link_1
        return self
