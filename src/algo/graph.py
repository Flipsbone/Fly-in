from src.models.network import Network
from src.algo.node import Node
from collections import deque
from typing import Any


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

    def _update_tab(
            self,
            tab: dict[str, dict[str, Any]],
            not_visited: list[str],
            current: str) -> str | None:

        if current in not_visited:
            not_visited.remove(current)

        for neighbor in self.nodes[current].neighbors:
            if tab[neighbor]["distance"] > (
                    tab[current]["distance"] + self.nodes[neighbor].cost):
                tab[neighbor] = {
                        "distance": (tab[current]["distance"] +
                                     self.nodes[neighbor].cost),
                        "from": current
                }
        mini: tuple[str | None, float] = (None, float('inf'))
        for node in not_visited:
            if tab[node]["distance"] < mini[1]:
                mini = (node, tab[node]["distance"])
        return mini[0]

    def solve(self) -> list[str]:
        path: list[str] = []
        current: str = self.start_name
        end: str = self.end_name
        tab: dict[str, dict[str, str | float | None]] = {}

        # neighbors = self.nodes[current].neighbors
        not_visited: list[str] = list(self.nodes.keys())

        for summit in not_visited:
            tab[summit] = {}
            if summit == current:
                tab[summit]["distance"] = 0
                tab[summit]["from"] = current
            else:
                tab[summit]["distance"] = float('inf')
                tab[summit]["from"] = None

        while current != end:
            new_current: str | None = (
                self._update_tab(tab, not_visited, current))
            if new_current is None:
                raise ValueError("none is not a node")
            current = new_current
        path = [end]
        current_step: str = end
        while current_step != self.start_name:
            prev_node = tab[current_step]["from"]
            if not isinstance(prev_node, str):
                print(tab)
                return []
            current_step = prev_node
            path.append(current_step)
        return path[::-1]
