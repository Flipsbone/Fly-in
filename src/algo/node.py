class Node:
    """Graph node storing zone attributes and adjacency.

    Attributes:
        name: Unique node name.
        zone_type: String describing zone behavior (e.g., 'priority').
        zone_color: Optional color name used by the visualizer.
        max_drones: Maximum allowed drones on this node per turn.
        neighbors: Mapping neighbor name -> link capacity.
        x, y: Coordinate values used for layout.
    """

    def __init__(
            self, name: str,
            zone_type: str,
            color: str | None,
            max_drones: int,
            x: int,
            y: int
            ) -> None:

        self.name = name
        self.zone_type = zone_type
        self.zone_color = color
        self.max_drones = max_drones
        self.neighbors: dict[str, int] = {}
        self.x = x
        self.y = y

    @property
    def cost(self) -> float:
        """Return the movement cost associated with this zone type.

        Higher cost indicates less-preferred zones (e.g., restricted).
        """
        match self.zone_type:
            case "restricted":
                return 2.0
            case "priority":
                return 1.0
            case "normal":
                return 1.0
            case _:
                return float('inf')

    def add_neighbor(self, neighbor_name: str, link_capacity: int) -> None:
        """Register a neighbor and the capacity of the connecting link.

        Args:
            neighbor_name: Name of the neighbor node.
            link_capacity: Maximum drones allowed on the link.
        """
        self.neighbors[neighbor_name] = link_capacity
