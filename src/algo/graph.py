from src.models.network import Network
from src.algo.node import Node
from src.algo.reservation_table import ReservationTable
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

    @staticmethod
    def _ceiling_round(x: float) -> float:
        return int(x) + (x > int(x))

    def _update_tab(
            self,
            tab: dict[tuple[int, str], dict[str, Any]],
            not_visited: list[tuple[int, str]],
            current: tuple[int, str],
            reservation: ReservationTable) -> tuple[int, str] | None:

        if current in not_visited:
            not_visited.remove(current)

        for neighbor in self.nodes[current[1]].neighbors:

            lap: int = current[0] + int(
                self._ceiling_round(self.nodes[neighbor].cost))

            if not reservation.is_available(lap,
                                            self.nodes[neighbor].name,
                                            self.nodes[neighbor].max_drones):
                continue

            if self.nodes[neighbor].zone_type == "restricted":
                route_turn = current[0] + 1
                route_key = (current[1], neighbor)
                route_capacity = self.nodes[current[1]].neighbors[neighbor]
                route_name = f"{route_key[0]}-{route_key[1]}"
                if not reservation.is_available(
                        route_turn, route_name, route_capacity):
                    continue
                if not reservation.is_available(
                    lap,
                    self.nodes[neighbor].name,
                        self.nodes[neighbor].max_drones):
                    continue

            if tab.get(
                (lap, neighbor), {"distance": float('inf')})["distance"] > (
                    tab[current]["distance"] + self.nodes[neighbor].cost):
                tab[lap, neighbor] = {
                        "distance": (tab[current]["distance"] +
                                     self.nodes[neighbor].cost),
                        "from": current
                }
                not_visited.append((lap, neighbor))
        wait_current = (current[0] + 1, current[1])
        if reservation.is_available(wait_current[0], wait_current[1],
                                    self.nodes[wait_current[1]].max_drones):
            if tab.get(
                wait_current, {"distance": float('inf')})["distance"] > (
                    tab[current]["distance"] + 0.9):

                tab[wait_current] = {
                    "distance": tab[current]["distance"] + 0.9,
                    "from": current
                }
                not_visited.append((wait_current))

        mini: tuple[tuple[int, str] | None, float] = (None, float('inf'))
        for node in not_visited:
            if tab[node]["distance"] < mini[1]:
                mini = (node, tab[node]["distance"])
        return mini[0]

    def solve(self, reservation: ReservationTable) -> list[str]:
        path: list[str] = []
        current: tuple[int, str] = (0, self.start_name)
        end: str = self.end_name
        not_visited: list[tuple[int, str]] = []
        tab: dict[tuple[int, str], dict[str, Any]] = {}

        not_visited.append((0, self.start_name))
        tab[current] = {
            "distance": 0,
            "from": current[1]
        }

        while current[1] != end:
            new_current: tuple[int, str] | None = (
                self._update_tab(tab, not_visited, current, reservation))
            if new_current is None:
                raise ValueError("none is not a node")
            current = new_current

        path = [end]
        current_step: tuple[int, str] = current
        path.append(current_step[1])
        while current_step != (0, self.start_name):
            prev_tuple = tab[current_step]["from"]
            if not isinstance(prev_tuple, tuple):
                print(tab)
                return []
            if current_step[0] - prev_tuple[0] == 2:
                connection_name: str = f"{prev_tuple[1]}-{current_step[1]}"
                path.append(connection_name)
            current_step = prev_tuple
            path.append(current_step[1])
        return path[::-1]
