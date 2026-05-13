from src.parser.map_validator import Zone_Approval, Connection_Approval
from collections import deque


class Network:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.zones: dict[str, Zone_Approval] = {}
        self.connections: dict[str, Connection_Approval] = {}
        self.start_node: Zone_Approval | None = None
        self.end_node: Zone_Approval | None = None
        self.used_coordinates: set[tuple[int, int]] = set()

    def naming_neighbors(self) -> dict[str, set[str]]:
        neighbors: dict[str, set[str]] = {zone: set() for zone in self.zones}
        for connection in self.connections.values():
            neighbors[connection.link_1].add(connection.link_2)
            neighbors[connection.link_2].add(connection.link_1)
        return neighbors

    def is_one_solution(self, neighbors: dict[str, set[str]]) -> bool:
        if self.start_node is None or self.end_node is None:
            return False
        queue: deque[str] = deque([])
        visited: set[str] = set()
        queue.append(self.start_node.name)
        visited.add(self.start_node.name)
        while (queue):
            current_position = queue.pop()
            print(current_position)
            if current_position == self.end_node.name:
                return True
            for neighbor in neighbors[current_position]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    if self.zones[neighbor].zone != "blocked":
                        queue.append(neighbor)
        return False
