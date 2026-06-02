from dataclasses import dataclass
from src.parser.map_validator import Zone_Approval, Connection_Approval


@dataclass
class DataMap:
    """Container for parsed map data.

    Attributes:
        nb_drones: Number of drones.
        zones: Mapping of zone name.
        connections: Mapping of connection.
        start_node: The starting hub zone.
        end_node: The ending hub zone.
        used_coordinates: Set of (x, y) to know exactly which coor. used
    """
    nb_drones: int
    zones: dict[str, Zone_Approval]
    connections: dict[str, Connection_Approval]
    start_node: Zone_Approval
    end_node: Zone_Approval
    used_coordinates: set[tuple[int, int]]
