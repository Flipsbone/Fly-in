from dataclasses import dataclass
from collections import deque
from typing import Any
import math
from src.algo.reservation_table import ReservationTable
from src.algo.graph import Graph


@dataclass(frozen=True, order=True)
class TimeNode:
    turn: int
    name: str


class PathFinder:
    def __init__(self, graph: Graph, reservation: ReservationTable):
        self.graph = graph
        self.reservation = reservation
        self.tab: dict[TimeNode, dict[str, Any]] = {}
        self.not_visited: list[TimeNode] = []

    def is_one_solution(self) -> bool:
        queue: deque[str] = deque([self.graph.start_name])
        visited: set[str] = {self.graph.start_name}

        while queue:
            current = queue.popleft()
            if current == self.graph.end_name:
                return True

            for neighbor_name in self.graph.nodes[current].neighbors:
                if neighbor_name not in visited:
                    visited.add(neighbor_name)
                    if self.graph.nodes[neighbor_name].zone_type != "blocked":
                        queue.append(neighbor_name)
        return False

    def _evaluate_neighbors(self, current: TimeNode) -> None:
        current_node = self.graph.nodes[current.name]

        for neighbor_name in current_node.neighbors:
            neighbor_node = self.graph.nodes[neighbor_name]
            lap = current.turn + math.ceil(neighbor_node.cost)

            if not self.reservation.is_available(
                    lap, neighbor_node.name, neighbor_node.max_drones):
                continue

            if neighbor_node.zone_type == "restricted":
                route_turn = current.turn + 1
                route_capacity = current_node.neighbors[neighbor_name]
                route_name = f"{current.name}-{neighbor_name}"
                if not self.reservation.is_available(
                        route_turn, route_name, route_capacity):
                    continue
                if not self.reservation.is_available(
                        lap, neighbor_node.name, neighbor_node.max_drones):
                    continue

            next_state = TimeNode(turn=lap, name=neighbor_name)
            new_distance = self.tab[current]["distance"] + neighbor_node.cost

            if self.tab.get(
                next_state,
                    {"distance": float('inf')})["distance"] > new_distance:

                self.tab[next_state] = {
                    "distance": new_distance,
                    "from": current
                }

                self.not_visited.append(next_state)

    def _evaluate_wait(self, current: TimeNode) -> None:
        current_node = self.graph.nodes[current.name]
        wait_state = TimeNode(turn=current.turn + 1, name=current.name)

        if self.reservation.is_available(
                wait_state.turn, wait_state.name, current_node.max_drones):
            wait_distance = self.tab[current]["distance"] + 0.9

            if self.tab.get(
                wait_state, {"distance": float('inf')})["distance"] > (
                    wait_distance):
                self.tab[wait_state] = {
                    "distance": wait_distance,
                    "from": current
                }
                self.not_visited.append(wait_state)

    def _get_next_closest_node(self) -> TimeNode | None:
        mini: tuple[TimeNode | None, float] = (None, float('inf'))
        for node in self.not_visited:
            if self.tab[node]["distance"] < mini[1]:
                mini = (node, self.tab[node]["distance"])
        return mini[0]

    def _process_node(self, current: TimeNode) -> TimeNode | None:
        if current in self.not_visited:
            self.not_visited.remove(current)

        self._evaluate_neighbors(current)
        self._evaluate_wait(current)

        return self._get_next_closest_node()

    def _reconstruct_path(
            self, end_state: TimeNode, start_state: TimeNode) -> list[str]:

        path: list[str] = [end_state.name]
        current_step = end_state

        while current_step != start_state:
            prev_step = self.tab[current_step]["from"]

            if current_step.turn - prev_step.turn == 2:
                connection_name = f"{prev_step.name}-{current_step.name}"
                path.append(connection_name)

            path.append(prev_step.name)
            current_step = prev_step

        return path[::-1]

    def solve(self) -> list[str]:
        start_state = TimeNode(turn=0, name=self.graph.start_name)
        current: TimeNode = start_state

        self.not_visited.append(current)
        self.tab[current] = {
            "distance": 0,
            "from": None
        }

        while current.name != self.graph.end_name:
            new_current = self._process_node(current)
            if new_current is None:
                raise ValueError("'new_current' can't be None")
            current = new_current

        return self._reconstruct_path(current, start_state)
