from src.parser.map_validator import Zone_Approval , Connection_Approval


class Network:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.zones: dict[str, Zone_Approval]= {}
        self.connections: dict[str, Connection_Approval] = {}
        self.start_node: Zone_Approval | None = None
        self.end_node: Zone_Approval | None = None
        self.used_coordinates: set[tuple[int, int]] = set()
