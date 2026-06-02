from dataclasses import dataclass, field


@dataclass
class DronePositions:
    """Positions of drones on nodes and links.

    Attributes:
        on_nodes: Mapping of node name to count of drones on that node.
        on_links: Mapping of link (node_a, node_b) to list of drone ids.
    """
    on_nodes: dict[str, int] = field(default_factory=dict)
    on_links: dict[tuple[str, str], list[int]] = field(default_factory=dict)


@dataclass
class HoveredNode:
    """Information about a node currently hovered by the mouse.

    Attributes:
        name: Node name shown in the tooltip.
        type: Zone type string (e.g., 'priority', 'normal').
        x: X coordinate on screen.
        y: Y coordinate on screen.
    """
    name: str
    type: str
    x: int
    y: int
