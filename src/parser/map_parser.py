from typing import TextIO
from pydantic import ValidationError

from src.parser.map_validator import (
    Drone_Approval,
    Zone_Approval,
    Connection_Approval
)

from src.models.network import Network


def _validate_parsed_map(
        start_hub: int, end_hub: int, my_map: Network) -> None:

    if start_hub != 1 or end_hub != 1:
        raise ValueError("Map must have exactly one start_hub and one end_hub")

    if my_map.start_node is None or my_map.end_node is None:
        raise ValueError("Parsing error: start_hub or "
                         "end_hub nodes were not properly initialized")

    if my_map.end_node.max_drones != my_map.nb_drones:
        raise ValueError(f"--- line {my_map.end_node.line} --- \n"
                         "Parsing error: end_hub max_drones "
                         f"({my_map.end_node.max_drones}) "
                         f"must be equal to nb_drones ({my_map.nb_drones})")

    if my_map.start_node.max_drones != my_map.nb_drones:
        raise ValueError(f"--- line {my_map.start_node.line} --- \n"
                         "Parsing error: start_hub max_drones "
                         f"({my_map.start_node.max_drones}) "
                         f"must be equal to nb_drones ({my_map.nb_drones})")


def parse_map(map_file: TextIO) -> Network:
    find_drones_line: bool = False
    clean_line_without_diez: str = ""
    start_hub: int = 0
    end_hub: int = 0
    my_map: Network = Network()

    for i, line in enumerate(map_file):
        i += 1
        clean_line: str = line.strip()

        if clean_line == "" or clean_line.startswith("#"):
            continue

        if ":" not in clean_line:
            raise ValueError(f"--- line {i} --- \n"
                             f"Invalid format : {clean_line}")

        if "#" in clean_line:
            clean_line_without_diez = clean_line.split("#")[0].strip()

        if clean_line_without_diez:
            extract_value: list[str] = clean_line_without_diez.split(":")
            clean_line_without_diez = ""
        else:
            extract_value = clean_line.split(":")

        if len(extract_value) > 2:
            raise ValueError(f"--- line {i} --- \n"
                             f"Invalid format in : {clean_line}")

        match extract_value[0].strip():

            case "nb_drones":
                if find_drones_line:
                    raise ValueError(f"--- line {i} --- \n"
                                     "Duplicate nb_drones")

                if not find_drones_line:
                    find_drones_line = True

                try:
                    value: int = int(extract_value[1].strip())
                    validate_drone: Drone_Approval = Drone_Approval(
                        nb_drones=value)
                    my_map.nb_drones = validate_drone.nb_drones
                except ValueError:
                    raise ValueError(f"--- line {i} --- \n"
                                     "Parsing error: drone "
                                     f"'{extract_value[1].strip()}' "
                                     f"must be integer > 0")

            case "start_hub" | "hub" | "end_hub":
                if not find_drones_line:
                    raise ValueError(f"--- line {i} --- \n Missing "
                                     "or misplaced 'nb_drones' it must be "
                                     "defined at the beginning of the file")

                if extract_value[0].strip() == "start_hub":
                    start_hub += 1
                if extract_value[0].strip() == "end_hub":
                    end_hub += 1
                if start_hub > 1 or end_hub > 1:
                    raise ValueError(f"--- line {i} --- \n"
                                     f"There must be exactly one"
                                     f"'{extract_value[0]}' be write")

                parts: list[str] = extract_value[1].strip().split(maxsplit=3)

                if len(parts) < 3:
                    raise ValueError(f"--- line {i} --- \n"
                                     f"Invalid format line: {clean_line}: must"
                                     " be <name> <x> <y> [metadata](optional)")

                try:
                    zone_data = {
                        "name": parts[0],
                        "x": parts[1],
                        "y": parts[2],
                        "metadata": parts[3] if len(parts) > 3 else "",
                        "line": i
                    }
                    validate_zone = Zone_Approval.model_validate(zone_data)
                    coords: tuple[int, int] = (
                        validate_zone.x, validate_zone.y)

                    if coords in my_map.used_coordinates:
                        raise ValueError(f"--- line {i} --- \n"
                                         "Parsing Error: "
                                         f"Duplicate coordinates '{coords}'")
                    my_map.used_coordinates.add(coords)
                    my_map.zones[validate_zone.name] = validate_zone
                    if extract_value[0].strip() == "start_hub":
                        my_map.start_node = validate_zone
                    if extract_value[0].strip() == "end_hub":
                        my_map.end_node = validate_zone
                except ValidationError as e:
                    msg = e.errors()[0]['msg']
                    raise ValueError(f"--- line {i} --- \n"
                                     f"Parsing Error : {msg}")

            case "connection":
                if not find_drones_line:
                    raise ValueError(f"--- line {i} --- \n Missing "
                                     "or misplaced 'nb_drones' it must be "
                                     "defined at the beginning of the file")

                connections_data: list[str] = (
                    extract_value[1].strip().split(maxsplit=2))

                if "-" not in connections_data[0]:
                    raise ValueError(f"--- line {i} --- \n"
                                     f"Invalid format line: {clean_line} : "
                                     "must be Connection1-Connection2 only ")

                list_connections: list[str] = connections_data[0].split("-")

                nb_connections: int = len(list_connections)

                if nb_connections > 2:
                    raise ValueError(f"--- line {i} --- \n"
                                     f"Invalid format line: {clean_line} : "
                                     "must be Connection1-Connection2 only ")

                try:
                    connections: dict[str, str] = {
                        "link_1": list_connections[0],
                        "link_2": list_connections[1],
                        "metadata": connections_data[1] if len(
                            connections_data) > 1 else ""
                    }
                    if (
                        list_connections[0] not in my_map.zones
                        or list_connections[1] not in my_map.zones
                    ):
                        raise ValueError(f"--- line {i} --- \n"
                                         "Connections must link only "
                                         "previously defined zones using")

                    validate_connection = Connection_Approval.model_validate(
                        connections)

                    unique_key: str = (
                        f"{validate_connection.link_1}-"
                        f"{validate_connection.link_2}"
                    )
                    if unique_key in my_map.connections:
                        raise ValueError(f"--- line {i} --- \n"
                                         f"Parsing Error: Duplicate connection"
                                         " '{unique_key}'")

                    my_map.connections[unique_key] = validate_connection
                except ValidationError as e:
                    msg = e.errors()[0]['msg']
                    raise ValueError(f"--- line {i} --- \n"
                                     f"Parsing Error : {msg}")

            case _:
                raise ValueError(f"--- line {i} --- \n"
                                 f"Invalid format line: {clean_line}\n"
                                 "ONLY CHOICES : \n"
                                 "nb_drones, start_hub, end_hub, hub "
                                 "or connection")

    _validate_parsed_map(
        start_hub,
        end_hub,
        my_map
    )

    return my_map
