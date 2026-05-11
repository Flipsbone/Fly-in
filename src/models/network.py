from src.parser.map_validator import Zone_Approval


class Network:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.zones: dict = {}
        self.connections: list = []
        self.start_node: Zone_Approval | None = None
        self.end_node: Zone_Approval | None = None
