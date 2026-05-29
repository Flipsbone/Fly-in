from src.models.data_map import DataMap
from src.algo.node import Node


class Graph:
    """Construct a graph from a `DataMap`.

    The constructor builds `Node` objects and connects them using the
    information from `network.connections`.
    """

    def __init__(self, network: DataMap) -> None:
        """Initialize graph nodes and record start/end names.

        Args:
            network: Parsed DataMap produced by the parser.
        """
        self.start_name: str = network.start_node.name
        self.end_name: str = network.end_node.name
        self.nodes: dict[str, Node] = {}
        self._build_graph(network)

    def _build_graph(self, network: DataMap) -> None:
        """Build graph with `self.nodes` and add neighbor relations.

        Args:
            network: DataMap used to create nodes and connections.
        """
        for name, zone in network.zones.items():
            self.nodes[name] = Node(
                name,
                zone.zone,
                zone.color,
                zone.max_drones,
                zone.x,
                zone.y
            )

        for name, connection in network.connections.items():
            self.nodes[connection.link_1].add_neighbor(
                connection.link_2, connection.max_link_capacity)
            self.nodes[connection.link_2].add_neighbor(
                connection.link_1, connection.max_link_capacity)
