class SimulationState:

    def __init__(self, drone_paths: dict[int, list[str]]) -> None:
        self.drone_paths = drone_paths
        self.current_turn: int = 0
        self.max_turn: int = self._calculate_max_turn()

    def _calculate_max_turn(self) -> int:
        if not self.drone_paths:
            return 0
        return max(len(path) for path in self.drone_paths.values()) - 1

    def next_turn(self) -> None:
        if self.current_turn < self.max_turn:
            self.current_turn += 1

    def previous_turn(self) -> None:
        if self.current_turn > 0:
            self.current_turn -= 1

    def get_drones_positions(self) -> tuple[
            dict[str, int], dict[tuple[str, str], list[int]]]:

        drones_on_nodes: dict[str, int] = {}
        drones_on_links: dict[tuple[str, str], list[int]] = {}

        for drone_id, path in self.drone_paths.items():
            if not path:
                continue

            t: int = min(self.current_turn, len(path) - 1)
            location: str = path[t]

            if '-' in location:
                try:
                    n1, n2 = location.split('-')
                    link_id: tuple[str, str] = min(n1, n2), max(n1, n2)

                    if link_id not in drones_on_links:
                        drones_on_links[link_id] = []
                    drones_on_links[link_id].append(drone_id)
                except ValueError:
                    pass
            else:
                drones_on_nodes[location] = drones_on_nodes.get(
                    location, 0) + 1

        return drones_on_nodes, drones_on_links
