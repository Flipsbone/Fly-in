import heapq
from dataclasses import dataclass
from collections import deque
from typing import Any
from src.algo.node import Node
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
        self.not_visited: list[tuple[float, TimeNode]] = []
        self.visited: set[TimeNode] = set()

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

    def _reconstruct_path(
            self, end_state: TimeNode, start_state: TimeNode) -> list[str]:

        path: list[str] = [end_state.name]
        current_step = end_state

        while current_step != start_state:
            prev_step: TimeNode = self.tab[current_step]["from"]
            path.append(prev_step.name)
            current_step = prev_step
        return path[::-1]

    def _maj_tab(
            self,
            current: TimeNode,
            neighbor_name: str,
            neigbor_node: Node,
            next_turn: int) -> None:

        next_state = TimeNode(next_turn, neighbor_name)
        new_weight = self.tab[current]["weight"] + neigbor_node.cost
        node_data = self.tab.get(next_state, {"weight": float('inf')})
        if new_weight < node_data["weight"]:
            self.tab[next_state] = {
                "weight": new_weight,
                "from": current
            }
            heapq.heappush(self.not_visited, (new_weight, next_state))

    def _evaluate_neighbors(self, current: TimeNode) -> None:
        self._wait(current)
        current_node: Node = self.graph.nodes[current.name]

        for neighbor_name, link_capacity in current_node.neighbors.items():

            neigbor_node: Node = self.graph.nodes[neighbor_name]
            if neigbor_node.zone_type == "blocked":
                continue

            next_turn: int = current.turn + 1

            route_name = (
                f"{min(current.name, neighbor_name)}-"
                f"{max(current.name, neighbor_name)}")
            if not self.reservation.is_available(
                    next_turn, route_name, link_capacity):
                continue

            if neigbor_node.zone_type == "restricted":
                if not self.reservation.is_available(
                        next_turn + 1,
                        route_name, link_capacity):
                    continue

                if not self.reservation.is_available(
                        next_turn + 1,
                        neigbor_node.name,
                        neigbor_node.max_drones):
                    continue

                new_weight = self.tab[current]["weight"] + neigbor_node.cost
                final_state = TimeNode(next_turn + 1, neighbor_name)
                node_data = self.tab.get(final_state, {"weight": float('inf')})

                if new_weight < node_data["weight"]:
                    connection_state = TimeNode(next_turn, route_name)
                    self.tab[connection_state] = {
                        "weight": self.tab[current]["weight"],
                        "from": current
                    }
                    self.tab[final_state] = {
                        "weight": new_weight,
                        "from": connection_state
                    }
                    heapq.heappush(self.not_visited, (new_weight, final_state))
            else:
                if not self.reservation.is_available(
                        next_turn, neigbor_node.name, neigbor_node.max_drones):
                    continue
                self._maj_tab(current, neighbor_name, neigbor_node, next_turn)

    def _wait(self, current: TimeNode) -> None:
        wait_turn = current.turn + 1
        new_weight = self.tab[current]["weight"] + 1
        wait_state = TimeNode(wait_turn, current.name)

        node_data = self.tab.get(wait_state, {"weight": float('inf')})
        if new_weight < node_data["weight"]:
            self.tab[wait_state] = {
                "weight": new_weight,
                "from": current
                }
            heapq.heappush(self.not_visited, (new_weight, wait_state))

    def solve(self) -> list[str]:
        start_state = TimeNode(turn=0, name=self.graph.start_name)
        current: TimeNode = start_state

        self.not_visited = []
        heapq.heappush(self.not_visited, (0, start_state))

        self.tab[current] = {
            "weight": 0,
            "from": None
        }
        while self.not_visited:
            current_weight, current = heapq.heappop(self.not_visited)
            if current.name == self.graph.end_name:
                return self._reconstruct_path(current, start_state)
            if current_weight > self.tab[current]["weight"]:
                continue
            if current in self.visited:
                continue
            self.visited.add(current)
            self._evaluate_neighbors(current)
        raise ValueError("No path found")
