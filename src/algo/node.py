class Node:
    def __init__(self, name: str, zone_type: str, max_drones: int):
        self.name = name
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.neighbors: dict[str, int] = {}

    @property
    def cost(self) -> float:
        match self.zone_type:
            case "restricted":
                return 2.0
            case "priority":
                return 0.1
            case "normal":
                return 1.0
            case _:
                return float('inf')

    def add_neighbor(self, neighbor_name: str, link_capacity: int) -> None:
        self.neighbors[neighbor_name] = link_capacity
