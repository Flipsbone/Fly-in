class ReservationTable:
    def __init__(self) -> None:
        self.reservation: dict[tuple[int, str], int] = {}

    def is_available(self, lap: int, node: str, capacity_max: int) -> bool:
        current_reservations = self.reservation.get((lap, node), 0)
        return current_reservations < capacity_max

    def reserve(
            self,
            lap: int,
            node: str,
            max_capacity: int | None = None
            ) -> None:
        self.reservation[(lap, node)] = (
            self.reservation.get((lap, node), 0) + 1)
