from dataclasses import dataclass
from collections import deque
from typing import Any
from src.algo.node import Node
from src.algo.reservation_table import ReservationTable
from src.algo.graph import Graph


@dataclass(frozen=True)
class TimeNode:
    turn: int
    name: str


class PathFinder:
    def __init__(self, graph: Graph, reservation: ReservationTable):
        self.graph = graph
        self.reservation = reservation
        self.tab: dict[TimeNode, dict[str, float]] = {}
        self.not_visited: list[TimeNode] = []
        self.visted: set[str] = set()

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
    
    def _get_next_closest_node(self) -> TimeNode | None:
        mini: tuple[TimeNode | None, float] = (None, float('inf'))
        for next_state in self.not_visited:
            if self.tab[next_state]["weight"] < mini[1]:
                mini = (next_state, self.tab[next_state]["weight"])
        return mini[0]

    def _reconstruct_path(
            self, end_state: TimeNode, start_state: TimeNode) -> list[str]:

        path: list[str] = [end_state.name]
        current_step = end_state

        while current_step != start_state:
            prev_step: TimeNode = self.tab[current_step]["from"]
            path.append(prev_step.name)
            current_step = prev_step
        return path[::-1]
    
    def _maj_tab(self, current: TimeNode, neighbor_name: str, neigbor_node: Node, next_turn: int) -> None:
            next_state = TimeNode(next_turn, neighbor_name)
            new_weight = self.tab[current]["weight"] + neigbor_node.cost
            node_data = self.tab.get(next_state, {"weight": float('inf')})
            if new_weight < node_data["weight"]:
                self.tab[next_state] = {
                    "weight": new_weight,
                    "from": current
                }
                self.not_visited.append(next_state)

    def _evaluate_neighbors(self, current: TimeNode) -> None:
        self._wait(current)
        current_node: Node = self.graph.nodes[current.name]

        for neighbor_name, link_capacity in current_node.neighbors.items():
            if neighbor_name in self.visted:
                continue

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
                    next_turn + 1, neigbor_node.name, neigbor_node.max_drones):
                    continue
                connection_state = TimeNode(next_turn, route_name)
                self.tab[connection_state] = {
                    "weight": self.tab[current]["weight"], 
                    "from": current
                }
                final_state = TimeNode(next_turn + 1, neighbor_name)
                self.tab[final_state] = {
                    "weight": self.tab[current]["weight"] + neigbor_node.cost,
                    "from": connection_state
                }
                self.not_visited.append(final_state)
            else:
                if not self.reservation.is_available(
                next_turn, neigbor_node.name, neigbor_node.max_drones):
                    continue
                self._maj_tab(current, neighbor_name, neigbor_node, next_turn)


    
    def _wait(self, current: TimeNode) -> None:
        current_node: Node = self.graph.nodes[current.name]
        wait_turn = current.turn + 1
        if current.name != self.graph.start_name:
            if not self.reservation.is_available(wait_turn, current.name, current_node.max_drones):
                return 

        new_weight = self.tab[current]["weight"] + 1
        wait_state = TimeNode(wait_turn, current.name)

        node_data = self.tab.get(wait_state, {"weight": float('inf')})
        if new_weight < node_data["weight"]:
            self.tab[wait_state] = {
                "weight": new_weight,
                "from": current
                }
        self.not_visited.append(wait_state)

    def _process_node(self, current: TimeNode) -> TimeNode:
        if current in self.not_visited:
            self.not_visited.remove(current)

        self._evaluate_neighbors(current)
        return self._get_next_closest_node()

    def solve(self) -> list[str]:
        start_state = TimeNode(turn=0, name=self.graph.start_name)
        current: TimeNode = start_state

        self.not_visited.append(current)
        self.tab[current] = {
            "weight": 0,
            "from": None
        }
        self.visted.add(current.name)

        while current.name != self.graph.end_name:
            new_state = self._process_node(current)
            if new_state is None:
                raise ValueError("'new_current' can't be None")
            current = new_state

        return self._reconstruct_path(current, start_state)
