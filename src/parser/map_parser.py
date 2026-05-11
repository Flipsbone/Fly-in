import sys
from typing import TextIO
from pydantic import ValidationError

from src.parser.map_validator import (
    Drone_Approval,
    Zone_Approval,
    Connection_Approval
)

from src.models.network import Network


def parse_map(map_file: TextIO) -> Network:
    find_drones_line = False
    start_hub = 0
    end_hub = 0
    my_map = Network()
    for i, line in enumerate(map_file):
        i += 1
        clean_line = line.strip()
        if clean_line == "" or clean_line.startswith("#"):
            continue
        if ":" not in clean_line:
            raise ValueError(f"--- line {i} --- \n"
                             f"Invalid format : {clean_line}")
        extract_value = clean_line.split(":")
        if len(extract_value) > 2:
            raise ValueError(f"--- line {i} --- \n"
                             f"Invalid format in : {clean_line}")

        match extract_value[0].strip():

            case "nb_drones":
                if find_drones_line:
                    raise ValueError(f"Line {i} Duplicate nb_drones")
                if not find_drones_line:
                    find_drones_line = True
                try:
                    value = int(extract_value[1].strip())
                    validate_drone = Drone_Approval(nb_drones=value)
                    my_map.nb_drones = validate_drone.nb_drones
                except ValueError:
                    raise ValueError(f"--- line {i} --- \n"
                                     f"Parsing error: drone '{extract_value[1].strip()}' "
                                     f"must be integer > 0")

            case "start_hub" | "hub" | "end_hub":
                if not find_drones_line:
                    raise ValueError("nb_drones must be at "
                                     "the beginning of the file")
                if extract_value[0].strip() == "start_hub":
                    start_hub += 1
                if extract_value[0].strip() == "end_hub":
                    end_hub += 1
                if start_hub > 1 or end_hub > 1:
                    raise ValueError(f"--- line {i} --- \n"
                                     f"There must be exactly one"
                                     f"'{extract_value[0]}' be write")
                parts = extract_value[1].strip().split(maxsplit=3)
                if len(parts) < 3:
                    raise ValueError (f"--- line {i} --- \n"
                                      f"Invalid format line: {clean_line} must be : "
                                      "<name> <x> <y> [metadata](optional)")
                try:
                    zone_data = {
                        "name": parts[0],
                        "x": parts[1],
                        "y": parts[2],
                        "metadata": parts[3] if len(parts) > 3 else ""
                    }
                    validate_zone = Zone_Approval.model_validate(zone_data)
                    my_map.zones[validate_zone.name] = validate_zone
                    if extract_value[0].strip() == "start_hub":
                        my_map.start_node = validate_zone
                    if extract_value[0].strip() == "end_hub":
                        my_map.end_node = validate_zone
                except ValidationError as e:
                    msg = e.errors()[0]['msg']
                    raise ValueError(f"--- line {i} --- \n Parsing Error : {msg}")

            case "connection":
                if not find_drones_line:
                    raise ValueError("nb_drones must be at "
                                     "the beginning of the file")
                connections_data = extract_value[1].strip().split(maxsplit=2)
                if "-" not in connections_data[0]:
                    raise ValueError (f"--- line {i} --- \n"
                                      f"Invalid format line: {clean_line} must be : "
                                      "Connection1-Connection2 only ")
 
                list_connections = connections_data[0].split("-")
                nb_connections = len(list_connections)
                if nb_connections > 2:
                    raise ValueError (f"--- line {i} --- \n"
                                      f"Invalid format line: {clean_line} must be : "
                                      "Connection1-Connection2 only ")

                try:
                    connections = {
                        "link_1": list_connections[0],
                        "link_2": list_connections[1],
                        "metadata": connections_data[1] if len(
                            connections_data) > 1 else ""
                    }
                    if not list_connections[0] in my_map.zones or not list_connections[1] in my_map.zones:
                        raise ValueError (f"--- line {i} --- \n"
                                          "Connections must link only previously defined zones using")
                    validate_connection = Connection_Approval.model_validate(
                        connections)
                    #BEFORE ADDING, CHECK IF IT EXISTS IN THE ORDER LINK1 LINK2 OR LINK2 LINK1 IN MYMAP.CONNECTIONS.KEYS
                    my_map.connections.append(validate_connection)
                except ValidationError as e:
                    msg = e.errors()[0]['msg']
                    raise ValueError(f"--- line {i} --- \n Parsing Error : {msg}")

            case _:
                raise ValueError (f"--- line {i} --- \n"
                                  f"Invalid format line: {clean_line}")

    if not find_drones_line:
        raise ValueError("nb_drones must be at "
                         "the beginning of the file")

    if start_hub != 1 or end_hub != 1:
        raise ValueError("Map must have exactly one start_hub and one end_hub")

    return my_map
