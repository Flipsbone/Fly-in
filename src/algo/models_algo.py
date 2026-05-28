from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class TimeNode:
    turn: int
    name: str


@dataclass
class PathRecord:
    weight: float
    come_from: TimeNode | None = None


@dataclass(order=True)
class QueueItem:
    weight: float
    # 0 if zone == priority
    is_not_priority: int
    # 0 if wait. Make sure to prioritize the wait state rather
    # than moving and coming back the next turn at the same place.
    is_move: int
    state: TimeNode
