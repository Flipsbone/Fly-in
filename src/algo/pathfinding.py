import heapq
from collections import deque
from src.algo.node import Node
from src.algo.reservation_table import ReservationTable
from src.algo.graph import Graph
from src.algo.models_algo import TimeNode, PathRecord, QueueItem


class PathFinder:
    """Find time-expanded routes using reservation constraints.

    The path finder respects node and link capacities stored in a
    `ReservationTable`. It builds a time-expanded search table and
    reconstructs the found path when the end state is reached.
    """

    def __init__(self, graph: Graph, reservation: ReservationTable):
        """Initialize the solver with a graph and a reservation table.

        Args:
            graph: Graph containing nodes and topology.
            reservation: ReservationTable used to check availability.
        """
        self.graph: Graph = graph
        self.reservation: ReservationTable = reservation
        self.tab: dict[TimeNode, PathRecord] = {}
        self.not_visited: list[QueueItem] = []
        self.visited: set[TimeNode] = set()

    def is_one_solution(self) -> bool:
        """Quick check if a basic path exists ignoring time.

        Performs a breadth-first search over nodes to see if the end
        node is reachable from the start node, ignoring reservations.

        Returns:
            True when there is at least a structural path, else False.
        """
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
                    if self.graph.nodes[current].neighbors[neighbor_name] != 0:
                        if self.graph.nodes[neighbor_name].max_drones != 0:
                            if (self.graph.nodes[neighbor_name].zone_type !=
                                    "blocked"):
                                queue.append(neighbor_name)
        return False

    def _reconstruct_path(
            self, end_state: TimeNode, start_state: TimeNode) -> list[str]:
        """Rebuild the path from `start_state` to `end_state`.

        The method returns a list of node and link names
        representing the route.
        """

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

    def _update_tab(
            self,
            current: TimeNode,
            neighbor_node: Node,
            next_turn: int) -> None:
        """Update internal tables when moving to a neighbor node.

        This pushes a new candidate state into the heap with the
        appropriate priority and updates weights in `self.tab`.
        """

        next_state = TimeNode(next_turn, neighbor_node.name)
        new_weight = self.tab[current].weight + neighbor_node.cost

        if (next_state not in self.tab
                or new_weight < self.tab[next_state].weight):
            self.tab[next_state] = PathRecord(
                weight=new_weight, come_from=current)

            heapq.heappush(self.not_visited, QueueItem(
                    weight=new_weight,
                    is_not_priority=(
                        0 if neighbor_node.zone_type == "priority" else 1),
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
        """Return True when the restricted path resources are free.

        The method checks both the link and the target node for the
        next two turns that a restricted crossing would require.
        """

        turns: tuple[int, int] = (next_turn + 1, next_turn + 2)
        resources: tuple[tuple[str, int], tuple[str, int]] = (
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
            neighbor_node: Node,
            next_turn: int,
            route_name: str,
            link_capacity: int) -> None:
        """Handle neighbor nodes with `restricted` zone type.

        Restricted nodes require reserving the intermediate link and
        an extra turn on the target node. This method pushes final
        states to the search heapq if resources are available.
        """

        if not self._restricted_path_available(
                next_turn, route_name, link_capacity, neighbor_node):
            return

        new_weight = self.tab[current].weight + neighbor_node.cost

        restricted_state = TimeNode(next_turn + 1, neighbor_node.name)
        connection_state = TimeNode(next_turn, route_name)
        if (restricted_state not in self.tab or
                new_weight < self.tab[restricted_state].weight):

            self.tab[connection_state] = PathRecord(
                weight=self.tab[current].weight,
                come_from=current
            )
            self.tab[restricted_state] = PathRecord(
                weight=new_weight,
                come_from=connection_state
            )

            heapq.heappush(self.not_visited, QueueItem(
                weight=new_weight,
                is_not_priority=1,
                is_move=1,
                state=restricted_state
            ))

    def _evaluate_neighbors(self, current: TimeNode) -> None:
        """Evaluate neighbors of `current` and push valid moves.

        The method checks each neighbor for capacity and zone rules
        then either schedules a normal move or handles restricted
        transitions specially.
        """
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
                    current,
                    neigbor_node,
                    next_turn,
                    route_name,
                    link_capacity
                )
            else:
                if not self.reservation.is_available(
                        next_turn, neigbor_node.name, neigbor_node.max_drones):
                    continue
                self._update_tab(
                    current, neigbor_node, next_turn)

    def _wait(self, current: TimeNode) -> None:
        """Schedule a wait action (stay on current node for one turn)."""
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
        """Run the search and return a list of visited names as a path.

        Returns:
            A path represented as a list of node or link identifiers.

        Raises:
            ValueError: If no path could be found under current
                reservation constraints.
        """
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
            current = current_item.state
            if current.name == self.graph.end_name:
                return self._reconstruct_path(current, start_state)
            if current in self.visited:
                continue
            self.visited.add(current)
            self._evaluate_neighbors(current)
        raise ValueError("No path found")
