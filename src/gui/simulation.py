from src.gui.models_gui import DronePositions


class SimulationState:

    def __init__(self, drone_paths: dict[int, list[str]]) -> None:
        self.drone_paths = drone_paths
        self.current_turn: int = 0
        self.max_turn: int = self._calculate_max_turn()

    def _calculate_max_turn(self) -> int:
        return max(len(path) for path in self.drone_paths.values()) - 1

    def next_turn(self) -> None:
        if self.current_turn < self.max_turn:
            self.current_turn += 1

    def previous_turn(self) -> None:
        if self.current_turn > 0:
            self.current_turn -= 1

    def get_drones_positions(self) -> DronePositions:
        positions = DronePositions()

        for drone_id, path in self.drone_paths.items():
            turn: int = min(self.current_turn, len(path) - 1)
            location: str = path[turn]

            if '-' in location:
                node_1, node_2 = location.split('-')
                link_id: tuple[str, str] = (
                    min(node_1, node_2), max(node_1, node_2))

                if link_id not in positions.on_links:
                    positions.on_links[link_id] = []
                positions.on_links[link_id].append(drone_id)
            else:
                positions.on_nodes[location] = positions.on_nodes.get(
                    location, 0) + 1

        return positions
