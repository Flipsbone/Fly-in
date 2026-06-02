from typing import TextIO
from pydantic import ValidationError

from src.parser.map_validator import (
    Drone_Approval,
    Zone_Approval,
    Connection_Approval
)

from src.models.data_map import DataMap


class MapParser:
    """Parse a textual map file into a `DataMap`.

    The parser checks format rules and uses pydantic validators to
    normalize and validate zone and connection metadata.
    """

    def __init__(self) -> None:
        self.nb_drones: int
        self.zones: dict[str, Zone_Approval] = {}
        self.connections: dict[str, Connection_Approval] = {}
        self.start_node: Zone_Approval | None = None
        self.end_node: Zone_Approval | None = None
        self.used_coordinates: set[tuple[int, int]] = set()
        self.used_hub: dict[str, int] = {}
        self.has_drones_line: bool = False
        self.start_hub_count: int = 0
        self.end_hub_count: int = 0

    def parse_map(self, map_file: TextIO) -> DataMap:
        """Read and parse `map_file` returning a `DataMap`.

        Args:
            map_file: Open text file to read lines from.

        Returns:
            `DataMap` with validated zones and connections.

        Raises:
            ValueError: On syntax errors or validation failures.
        """

        flag_start_hub: bool = False
        flag_end_hub: bool = False

        for i, line in enumerate(map_file):
            i += 1
            clean_line: str = line.strip()

            if clean_line == "" or clean_line.startswith("#"):
                continue

            if ":" not in clean_line:
                raise ValueError(f"--- line {i} --- \n"
                                 f"Invalid format : {clean_line} "
                                 "must have one ':' after naming")

            clean_line_without_hash = clean_line.split("#")[0].strip()
            extract_value: list[str] = clean_line_without_hash.split(":")

            if len(extract_value) != 2:
                raise ValueError(f"--- line {i} --- \n"
                                 f"Invalid format : {clean_line} "
                                 "too many ':' only one")

            keyword: str = extract_value[0].strip()
            value_str: str = extract_value[1].strip()

            match keyword:

                case "nb_drones":
                    self._parse_nb_drones(value_str, i)
                case "start_hub":
                    flag_start_hub = True
                    self._parse_hub(keyword, value_str, clean_line, i)
                case "hub":
                    self._parse_hub(keyword, value_str, clean_line, i)
                case "end_hub":
                    flag_end_hub = True
                    self._parse_hub(keyword, value_str, clean_line, i)
                case "connection":
                    self._parse_connection(value_str, clean_line, i)
                case _:
                    raise ValueError(f"--- line {i} --- \n"
                                     f"Invalid format line: {clean_line}\n"
                                     "ONLY CHOICES : \n"
                                     "'nb_drones:' , 'start_hub:' , 'end_hub:'"
                                     " , 'hub:' or 'connection:' ")

        if not flag_start_hub:
            raise ValueError("Missing start_hub\n"
                             "Must be start_hub: "
                             "<name> <x> <y> [metadata](optional)")
        if not flag_end_hub:
            raise ValueError("Missing end_hub\n"
                             "Must be end_hub: "
                             "<name> <x> <y> [metadata](optional)")

        valid_start, valid_end = self._validate_parsed_map()

        return DataMap(
            nb_drones=self.nb_drones,
            zones=self.zones,
            connections=self.connections,
            start_node=valid_start,
            end_node=valid_end,
            used_coordinates=self.used_coordinates
        )

    def _parse_nb_drones(self, value_str: str, line_number: int) -> None:
        """Parse and validate the `nb_drones` line.

        Ensures the value is an integer and within allowed limits.
        """
        if self.has_drones_line:
            raise ValueError(f"--- line {line_number} --- \n"
                             "Duplicate nb_drones")

        self.has_drones_line = True

        try:
            nb_drones: int = int(value_str)
            validate_drone: Drone_Approval = Drone_Approval(
                nb_drones=nb_drones)
            self.nb_drones = validate_drone.nb_drones
        except ValueError:
            raise ValueError(
                    f"--- line {line_number} --- \n"
                    f"Parsing error: drone '{value_str}' must be integer > 0"
                )
        else:
            if nb_drones > 500:
                raise ValueError(
                    f"--- line {line_number} --- \n"
                    "nb_drones to high value must be under 500")

    def _parse_hub(
            self,
            hub_type: str,
            value_str: str,
            clean_line: str,
            line_number: int) -> None:
        """Parse a hub or start/end hub line and validate it.

        The method also enforces that `nb_drones` was defined before
        any hub lines.
        """

        if not self.has_drones_line:
            raise ValueError(f"--- line {line_number} --- \n Missing "
                             "or misplaced 'nb_drones' it must be "
                             "defined at the beginning of the file")

        if hub_type == "start_hub":
            self.start_hub_count += 1
        elif hub_type == "end_hub":
            self.end_hub_count += 1

        if self.start_hub_count > 1 or self.end_hub_count > 1:
            raise ValueError(
                f"--- line {line_number} --- \n"
                f"There must be exactly one '{hub_type}' be write"
                )
        parts: list[str] = value_str.split(maxsplit=3)

        if len(parts) < 3:
            raise ValueError(f"--- line {line_number} --- \n"
                             f"Invalid format line: {clean_line}: must"
                             " be <name> <x> <y> [metadata](optional)")
        try:
            zone_data = {
                "name": parts[0],
                "x": parts[1],
                "y": parts[2],
                "metadata": parts[3] if len(parts) > 3 else "",
                "line": line_number
            }
            validate_zone = Zone_Approval.model_validate(zone_data)
            if zone_data.get("name") in self.used_hub:
                original_line = self.used_hub[parts[0]]
                raise ValueError(f"--- line {line_number} --- \n"
                                 "Duplicate hub with "
                                 f"line {original_line}")
            else:
                self.used_hub[parts[0]] = line_number

            coords: tuple[int, int] = (
                validate_zone.x, validate_zone.y)

            if coords in self.used_coordinates:
                raise ValueError(f"--- line {line_number} --- \n"
                                 "Parsing Error: "
                                 f"Duplicate coordinates '{coords}'")
            self.used_coordinates.add(coords)
            self.zones[validate_zone.name] = validate_zone

            if hub_type == "start_hub":
                self.start_node = validate_zone
            elif hub_type == "end_hub":
                self.end_node = validate_zone
        except ValidationError as e:
            msg = e.errors()[0]['msg']
            raise ValueError(f"--- line {line_number} --- \n"
                             f"Parsing Error : {msg}")

    def _parse_connection(
            self,
            value_str: str,
            clean_line: str,
            line_number: int
            ) -> None:

        if not self.has_drones_line:
            raise ValueError(
                f"--- line {line_number} --- \n"
                "Missing or misplaced 'nb_drones' "
                "it must be defined at the beginning of the file"
            )

        connections_data: list[str] = value_str.split(maxsplit=2)

        if not connections_data or "-" not in connections_data[0]:
            raise ValueError(
                f"--- line {line_number} --- \n"
                f"Invalid format line: {clean_line} : "
                "must be Connection1-Connection2 only"
            )

        list_connections: list[str] = connections_data[0].split("-")

        if len(list_connections) > 2:
            raise ValueError(
                f"--- line {line_number} --- \n"
                f"Invalid format line: {clean_line} : "
                "must be Connection1-Connection2 only"
            )

        try:
            connections: dict[str, str] = {
                "link_1": list_connections[0],
                "link_2": list_connections[1],
                "metadata": connections_data[1] if len(
                    connections_data) > 1 else ""
            }

            if (list_connections[0] not in self.zones or
                    list_connections[1] not in self.zones):
                raise ValueError(
                    f"--- line {line_number} --- \n"
                    "Connections must link only previously defined zones"
                )

            validate_connection = Connection_Approval.model_validate(
                connections)

            unique_key: str = (f"{validate_connection.link_1}-"
                               f"{validate_connection.link_2}")
            if unique_key in self.connections:
                raise ValueError(
                    f"--- line {line_number} --- \n"
                    f"Parsing Error: Duplicate connection '{unique_key}'"
                )
            self.connections[unique_key] = validate_connection

        except ValidationError as e:
            msg = e.errors()[0]['msg']
            raise ValueError(f"--- line {line_number} --- \n"
                             f"Parsing Error : {msg}")

    def _validate_parsed_map(self) -> tuple[Zone_Approval, Zone_Approval]:
        """Final validation and normalization after parsing all lines.

        This method enforces single start/end hubs and sets hub
        capacities to the parsed number of drones.
        """

        if self.start_hub_count != 1 or self.end_hub_count != 1:
            raise ValueError("Map must have exactly one start_hub"
                             "and one end_hub")

        if self.start_node is None or self.end_node is None:
            raise ValueError("Parsing error: start_hub or "
                             "end_hub nodes were not properly initialized")

        self.start_node.max_drones = self.nb_drones
        self.end_node.max_drones = self.nb_drones

        return self.start_node, self.end_node
