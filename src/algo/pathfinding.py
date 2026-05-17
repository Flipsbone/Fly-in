from src.models.network import Network
from collections import deque


class SpaceTimePathfinder:
    def __init__(self, network: Network) -> None:
        self.network = network
        self.neighbors = self.network.naming_neighbors()

    def solve_path(self) -> bool:
        if self.network.start_node is None or self.network.end_node is None:
            return False
        start_state: tuple[str, float] = (self.network.start_node.name, 0)
        queue: deque[str] = deque([])
        visited: set[str] = set()
        came_from: dict[str, tuple[str, float]] = {
            self.network.start_node.name: start_state}
        queue.append(self.network.start_node.name)
        visited.add(self.network.start_node.name)
        while queue:
            current_position = queue.popleft()
            priority = came_from[current_position][1]
            if summits == visited:
                return True
            for neighbor in self.neighbors[current_position]:
                zone_type = self.network.zones[neighbor].zone
                if zone_type == "blocked":
                    continue
                match zone_type:
                    case "normal":
                        current_state: tuple[str, float] = (
                            current_position, 1 + priority)
                    case "restricted":
                        current_state = (current_position, 1 + priority)
                    case "priority":
                        current_state = (current_position, 0.1 + priority)
                    case _:
                        current_state = (current_position, 1 + priority)
                came_from[neighbor] = current_state
                print(came_from[neighbor])
        return True
