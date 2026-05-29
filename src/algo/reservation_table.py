class ReservationTable:
    """Track reserved resources per time step.

    The table maps `(lap, resource_name)` to the number of
    reservations already made for that resource at that time.
    """

    def __init__(self) -> None:
        self.reservation: dict[tuple[int, str], int] = {}

    def is_available(self, lap: int, node: str, capacity_max: int) -> bool:
        """Return True if `node` has capacity at `lap`.

        Args:
            lap: Time step index to check.
            node: Resource key (node or link name).
            capacity_max: Maximum allowed concurrent reservations.

        Returns:
            True when a new reservation can be made.
        """
        current_reservations = self.reservation.get((lap, node), 0)
        return current_reservations < capacity_max

    def reserve(self, lap: int, node: str) -> None:
        """Add one reservation for `node` at time `lap`."""
        self.reservation[(lap, node)] = (
            self.reservation.get((lap, node), 0) + 1)
