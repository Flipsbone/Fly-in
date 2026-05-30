from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class TimeNode:
    """A node in the time-expanded graph.

    Attributes:
        turn: Turn index.
        name: Name of the graph node or a link identifier.
    """
    turn: int
    name: str


@dataclass
class PathRecord:
    """Record of best-known cost and predecessor for a state.

    Attributes:
        weight: Accumulated cost to reach this state.
        come_from: Previous `TimeNode` in the best path.
    """
    weight: float
    come_from: TimeNode | None = None


@dataclass(order=True)
class QueueItem:
    """Item stored on the heap during search.

    Fields order controls heap comparison. Lower `weight` is
    prioritized;
    `is_not_priority` -> 0 if zone == priority
    and
    `is_move` -> 0 if wait. Make sure to prioritize the wait state rather
            than moving and coming back the next turn at the same place.
    """
    weight: float
    is_not_priority: int
    is_move: int
    state: TimeNode
