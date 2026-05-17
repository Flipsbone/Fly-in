class Node:
    def __init__(self, name: str):
        self.name = name
        self.neighbors: dict[Node, float] = {}

    def add_neighors(self, node: 'Node', weight: float) -> None:
        self.neighbors[node] = weight
