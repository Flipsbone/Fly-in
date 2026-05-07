import sys
from typing import TextIO

from src.parser.map_validator import (
    Drone_Approval,
    Zone_Approval,
    Connection_Approval
)
from pydantic import ValidationError


def main(map_file: TextIO) -> int:
    find_drones_line = False
    start_hub = 0
    end_hub = 0
    for i, line in enumerate(map_file):
        i += 1
        clean_line = line.strip()
        if clean_line == "" or clean_line.startswith("#"):
            continue
        if ":" not in clean_line:
            print(f"--- line {i} --- \n"
                  f"Invalid format : {clean_line}", file=sys.stderr)
            return (-1)
        extract_value = clean_line.split(":")
        if len(extract_value) > 2:
            print(f"--- line {i} --- \n"
                  f"Invalid format in : {clean_line}", file=sys.stderr)
            return (-1)
        match extract_value[0].strip():

            case "nb_drones":
                if find_drones_line:
                    raise ValueError(f"Line {i} Duplicate nb_drones")
                if not find_drones_line:
                    find_drones_line = True
                try:
                    value = int(extract_value[1].strip())
                    validate_drone = Drone_Approval(nb_drones=value)
                    number_drones = validate_drone.nb_drones
                    print(number_drones)
                except ValueError:
                    print(f"--- line {i} --- \n"
                          f"Parsing error: drone '{extract_value[1].strip()}' "
                          f"must be integer > 0", file=sys.stderr)
                    return (-1)

            case "start_hub" | "hub" | "end_hub":
                if not find_drones_line:
                    raise ValueError("nb_drones must be at "
                                     "the beginning of the file")
                if extract_value[0].strip() == "start_hub":
                    start_hub += 1
                if extract_value[0].strip() == "end_hub":
                    end_hub += 1
                if start_hub | end_hub > 1:
                    raise ValueError(f"--- line {i} --- \n"
                                     f"There must be exactly one"
                                     f"'{extract_value[0]}' be write")
                parts = extract_value[1].strip().split(maxsplit=3)
                if len(parts) < 3:
                    print(f"--- line {i} --- \n"
                          f"Invalid format line: {clean_line} must be : "
                          "<name> <x> <y> [metadata](optional)",
                          file=sys.stderr)
                    return (-1)
                try:
                    zone_data = {
                        "name": parts[0],
                        "x": parts[1],
                        "y": parts[2],
                        "metadata": parts[3] if len(parts) > 3 else ""
                    }
                    validate_zone = Zone_Approval.model_validate(zone_data)
                    print(validate_zone)
                except ValidationError as e:
                    for error in e.errors():
                        msg = error['msg']
                        print(f"--- line {i} --- \n"
                              f"Parsing Error on line {i}'{clean_line}': "
                              f"{msg}", file=sys.stderr)
                    return (-1)

            case "connection":
                if not find_drones_line:
                    raise ValueError("nb_drones must be at "
                                     "the beginning of the file")
                connections_data = extract_value[1].strip().split(maxsplit=2)
                if "-" not in connections_data[0]:
                    print(f"--- line {i} --- \n"
                          f"Invalid format line: {clean_line} must be : "
                          "Connection1-Connection2 only ", file=sys.stderr)
                    return (-1)
                list_connections = connections_data[0].split("-")
                nb_connections = len(list_connections)
                if nb_connections > 2:
                    print(f"--- line {i} --- \n"
                          f"Invalid format line: {clean_line} must be : "
                          "Connection1-Connection2 only ", file=sys.stderr)
                    return (-1)
                try:
                    connections = {
                        "link_1": list_connections[0],
                        "link_2": list_connections[1],
                        "metadata": connections_data[1] if len(
                            connections_data) > 1 else ""
                    }
                    validate_connection = Connection_Approval.model_validate(
                        connections)
                    print(validate_connection)
                except ValidationError as e:
                    for error in e.errors():
                        msg = error['msg']
                        print(f"--- line {i} --- \n"
                              f"Parsing Error on line '{clean_line}': "
                              f"{msg}", file=sys.stderr)
                    return (-1)
            case _:
                print(f"--- line {i} --- \n"
                      f"Invalid format line: {clean_line}", file=sys.stderr)
                return (-1)
    return (0)


if __name__ == "__main__":
    try:
        with open("maps/hard/02_capacity_hell.txt", "r") as map_file:
            main(map_file)
    except PermissionError as e:
        print(f"ERROR: {e}.", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"ERROR: {e} not found.", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
