from src.models.network import Network
from src.algo.node import Node
from collections import deque


class Graph:
    def __init__(self, network: Network) -> None:
        if network.start_node is None or network.end_node is None:
            raise ValueError("start_node.name or end_node.name invalid")
        self.start_name: str = network.start_node.name
        self.end_name: str = network.end_node.name
        self.nodes: dict[str, Node] = {}
        self._build_graph(network)

    def _build_graph(self, network: Network) -> None:
        for name, zone in network.zones.items():
            self.nodes[name] = Node(
                name,
                zone.zone,
                zone.color,
                zone.max_drones
            )

        for name, connection in network.connections.items():
            node1 = self.nodes[connection.link_1]
            node2 = self.nodes[connection.link_2]
            node1.add_neighbor(connection.link_2, connection.max_link_capacity)
            node2.add_neighbor(connection.link_1, connection.max_link_capacity)

    def is_one_solution(self) -> bool:
        if self.start_name is None or self.end_name is None:
            return False
        queue: deque[str] = deque([])
        visited: set[str] = set()
        queue.append(self.start_name)
        visited.add(self.start_name)
        while (queue):
            current_position = queue.popleft()
            if current_position == self.end_name:
                return True
            for neighbor in self.nodes[current_position].neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    if self.nodes[neighbor].zone_type != "blocked":
                        queue.append(neighbor)
        return False

    # def solve(self) -> list[str]:
    #     path: list[str] = []
    #     current = self.start_name
    #     end = self.end_name
    #     tab: dict[str, float | str] = {
    #         "distance": 0.0,
    #         "from": current
    #     }

    #     neighbors = self.nodes[current].neighbors
    #     print(neighbors)
    #     not_visited: list[str] = list(self.nodes.keys())
    #     print(not_visited)

    #     while current != end:
    #         current = update_tab(self, tab, not_visited, current)

    #     return path

    # def update_tab(
    # self, tab: dict[float, str], not_visited: list[str], current: str):
    #     for neighbour in self.nodes[current].neighbors:
    #         if tab[neighbour][""]
