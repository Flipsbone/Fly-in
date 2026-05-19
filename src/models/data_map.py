from dataclasses import dataclass
from src.parser.map_validator import Zone_Approval, Connection_Approval


@dataclass
class DataMap:
    nb_drones: int
    zones: dict[str, Zone_Approval]
    connections: dict[str, Connection_Approval]
    start_node: Zone_Approval
    end_node: Zone_Approval
    used_coordinates: set[tuple[int, int]]
