import heapq
from collections import deque
from src.algo.node import Node
from src.algo.reservation_table import ReservationTable
from src.algo.graph import Graph
from src.algo.models_algo import TimeNode, PathRecord, QueueItem


class PathFinder:
    def __init__(self, graph: Graph, reservation: ReservationTable):
        self.graph: Graph = graph
        self.reservation: ReservationTable = reservation
        self.tab: dict[TimeNode, PathRecord] = {}
        self.not_visited: list[QueueItem] = []
        self.visited: set[TimeNode] = set()

    def is_one_solution(self) -> bool:
        queue: deque[str] = deque([self.graph.start_name])
        visited: set[str] = {self.graph.start_name}

        if self.graph.nodes[self.graph.start_name].zone_type == "blocked":
            return False

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
        current_step: TimeNode = end_state

        while current_step != start_state:
            prev_step = self.tab[current_step].come_from
            if prev_step is None:
                raise ValueError(
                    f"Path broken: {current_step} has no predecessor.")
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
        new_weight = self.tab[current].weight + neigbor_node.cost

        if (next_state not in self.tab
                or new_weight < self.tab[next_state].weight):
            self.tab[next_state] = PathRecord(
                weight=new_weight, come_from=current)

        heapq.heappush(self.not_visited, QueueItem(
                weight=new_weight,
                is_not_priority=(
                    0 if neigbor_node.zone_type == "priority" else 1),
                is_move=1,
                state=next_state
            ))

    def _restricted_path_available(
            self,
            next_turn: int,
            route_name: str,
            link_capacity: int,
            neighbor_node: Node,
            ) -> bool:

        turns = (next_turn + 1, next_turn + 2)
        resources = (
            (route_name, link_capacity),
            (neighbor_node.name, neighbor_node.max_drones),
        )

        return all(
            self.reservation.is_available(turn, res_name, res_capacity)
            for turn in turns
            for res_name, res_capacity in resources
        )

    def _process_restricted_neighbor(
            self, current: TimeNode,
            neighbor_name: str, neigbor_node: Node,
            next_turn: int, route_name: str,
            link_capacity: int) -> None:

        if not self._restricted_path_available(
                next_turn, route_name, link_capacity, neigbor_node):
            return

        new_weight = self.tab[current].weight + neigbor_node.cost
        final_state = TimeNode(next_turn + 1, neighbor_name)

        if (final_state not in self.tab or
                new_weight < self.tab[final_state].weight):

            connection_state = TimeNode(next_turn, route_name)

            self.tab[connection_state] = PathRecord(
                weight=self.tab[current].weight,
                come_from=current
            )
            self.tab[final_state] = PathRecord(
                weight=new_weight,
                come_from=connection_state
            )

            heapq.heappush(self.not_visited, QueueItem(
                weight=new_weight,
                is_not_priority=1,
                is_move=1,
                state=final_state
            ))

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
                self._process_restricted_neighbor(
                    current, neighbor_name,
                    neigbor_node, next_turn,
                    route_name, link_capacity
                )
            else:
                if not self.reservation.is_available(
                        next_turn, neigbor_node.name, neigbor_node.max_drones):
                    continue
                self._maj_tab(current, neighbor_name, neigbor_node, next_turn)

    def _wait(self, current: TimeNode) -> None:
        wait_turn = current.turn + 1
        new_weight = self.tab[current].weight + 1
        wait_state = TimeNode(wait_turn, current.name)
        if (wait_state not in self.tab or
                new_weight < self.tab[wait_state].weight):

            self.tab[wait_state] = PathRecord(
                weight=new_weight,
                come_from=current)

            heapq.heappush(self.not_visited, QueueItem(
                weight=new_weight,
                is_not_priority=(
                    0 if self.graph.nodes[current.name].zone_type ==
                    "priority" else 1),
                is_move=0,
                state=wait_state
            ))

    def solve(self) -> list[str]:
        start_state: TimeNode = TimeNode(turn=0, name=self.graph.start_name)
        current: TimeNode = start_state

        heapq.heappush(self.not_visited, QueueItem(
            weight=0.0,
            is_not_priority=(
                0 if self.graph.nodes[self.graph.start_name].zone_type ==
                "priority" else 1),
            is_move=0,
            state=start_state
        ))

        self.tab[current] = PathRecord(
                weight=0,
                come_from=None)

        while self.not_visited:
            current_item = heapq.heappop(self.not_visited)
            current_weight = current_item.weight
            current = current_item.state
            if current.name == self.graph.end_name:
                return self._reconstruct_path(current, start_state)
            if current_weight > self.tab[current].weight:
                continue
            if current in self.visited:
                continue
            self.visited.add(current)
            self._evaluate_neighbors(current)
        raise ValueError("No path found")
