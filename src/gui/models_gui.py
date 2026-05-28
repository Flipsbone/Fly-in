from dataclasses import dataclass, field


@dataclass
class DronePositions:
    on_nodes: dict[str, int] = field(default_factory=dict)
    on_links: dict[tuple[str, str], list[int]] = field(default_factory=dict)


@dataclass
class HoveredNode:
    name: str
    type: str
    x: int
    y: int
