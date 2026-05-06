import sys
from typing import TextIO

from src.parser.map_validator import (
    Drone_Approval,
    Zone_Approval,
    Connection_Approval
)
from pydantic import ValidationError


def main(map_file: TextIO) -> int:
    for line in map_file:
        clean_line = line.strip()
        if clean_line == "" or clean_line.startswith("#"):
            continue
        if ":" not in clean_line:
            print(f"Invalid format line: {clean_line}", file=sys.stderr)
            return (-1)
        extract_value = clean_line.split(":")
        if len(extract_value) > 2:
            print(f"Invalid format in line: {clean_line}", file=sys.stderr)
            return (-1)
        match extract_value[0].strip():

            case "nb_drones":
                try:
                    value = int(extract_value[1].strip())
                    validate_drone = Drone_Approval(nb_drones=value)
                    number_drones = validate_drone.nb_drones
                    print(number_drones)
                except ValueError:
                    print(f"Parsing error: drone '{extract_value[1].strip()}' "
                          f"must be integer > 0", file=sys.stderr)
                    return (-1)

            case "start_hub" | "hub" | "end_hub":
                parts = extract_value[1].strip().split(maxsplit=3)
                if len(parts) < 3:
                    print(f"Invalid format line: {clean_line} must be : "
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
                        print(f"Parsing Error on line '{clean_line}': "
                              f"{msg}", file=sys.stderr)
                    return (-1)

            case "connection":
                connections_data = extract_value[1].strip().split(maxsplit=2)
                if "-" not in connections_data[0]:
                    print(f"Invalid format line: {clean_line} must be : "
                          "Connection1-Connection2 only ", file=sys.stderr)
                    return (-1)
                connections = connections_data[0].split("-")
                nb_connections = len(connections)
                if nb_connections > 2:
                    print(f"Invalid format line: {clean_line} must be : "
                          "Connection1-Connection2 only ", file=sys.stderr)
                    return (-1)
                validate_connection = Connection_Approval.model_validate(
                    connections)
                print(validate_connection)
            case _:
                print(f"Invalid format line: {clean_line}", file=sys.stderr)
                return (-1)
    return (0)


if __name__ == "__main__":
    try:
        with open("maps/easy/01_linear_path.txt", "r") as map_file:
            main(map_file)
    except PermissionError as e:
        print(f"ERROR: {e}.", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"ERROR: {e} not found.", file=sys.stderr)
    except Exception as e:
        print(f"RESPONSE: Unexpected anomaly: {e}", file=sys.stderr)
