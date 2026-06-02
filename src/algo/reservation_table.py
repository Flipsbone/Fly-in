class ReservationTable:
    """Track reserved resources per time step.

    The table maps `(lap, resource_name)` to the number of
    reservations already made for that resource at that time.
    """

    def __init__(self) -> None:
        self.reservation: dict[tuple[int, str], int] = {}
        self.parked: list[tuple[int, str]] = []

    def is_available(self, lap: int, node: str, capacity_max: int) -> bool:
        """Return True if `node` has capacity at `lap`.

        Args:
            lap: Time step index to check.
            node: Resource key (node or link name).
            capacity_max: Maximum allowed concurrent reservations.

        Returns:
            True when a new reservation can be made.
        """
        return self.get_total_drones(lap, node) < capacity_max

    def reserve(self, lap: int, node: str) -> None:
        """Add one reservation for `node` at time `lap`."""
        self.reservation[(lap, node)] = (
            self.reservation.get((lap, node), 0) + 1)

    def get_total_drones(self, lap: int, node: str) -> int:
        """Calculate the total number of drones on a node at a given turn.
        Args:
            lap (int): The specific turn or time step to evaluate.
            node (str): The identifier of the node or link.

        Returns:
            int: The total number of drones occupying a node at that turn.
        """
        total = self.reservation.get((lap, node), 0)
        for arrival_lap, parked_node in self.parked:
            if parked_node == node and lap > arrival_lap:
                total += 1
        return total

    def park(self, path: list[str]) -> None:
        """Record a drone's permanent parking location after completing
        its route.

        Args:
            path (list[str]): The complete sequence of nodes and links
                traversed by the drone.
        """
        arrival_lap = len(path) - 1
        final_node = path[-1]
        self.parked.append((arrival_lap, final_node))
