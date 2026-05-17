from src.models.network import Network
from src.algo.node import Node


class Graph:
    def __init__(self, network: Network) -> None:
        if network.start_node is None or network.end_node is None:
            raise ValueError("start_node.name or end_node.name invalid")
        self.start_name: str = network.start_node.name
        self.end_name: str = network.end_node.name
        self.nodes: dict[str, Node] = {}
        self._build_graph(network)

    def _build_graph(self, network: Network) -> None:
        for name, zone in network.zones.items():
            self.nodes[name] = Node(
                name,
                zone.zone,
                zone.max_drones
            )

        for name, connection in network.connections.items():
            node1 = self.nodes[connection.link_1]
            node2 = self.nodes[connection.link_2]
            node1.add_neighbor(connection.link_2, connection.max_link_capacity)
            node2.add_neighbor(connection.link_1, connection.max_link_capacity)