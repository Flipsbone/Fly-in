from src.algo.graph import Graph


class GraphLayout:

    def __init__(self, graph: Graph, padding: int) -> None:
        self.graph = graph
        self.padding = padding
        self.screen_coords: dict[str, tuple[int, int]] = {}

    def recalculate(self, window_width: int, window_height: int) -> None:
        min_x: float = min(node.x for node in self.graph.nodes.values())
        max_x: float = max(node.x for node in self.graph.nodes.values())
        min_y: float = min(node.y for node in self.graph.nodes.values())
        max_y: float = max(node.y for node in self.graph.nodes.values())

        drawable_width: int = window_width - (2 * self.padding)
        drawable_height: int = window_height - (2 * self.padding)

        range_x: float = max(1.0, float(max_x - min_x))
        range_y: float = max(1.0, float(max_y - min_y))

        for name, node in self.graph.nodes.items():
            screen_x = int(
                self.padding + ((node.x - min_x) / range_x) * drawable_width
            )
            screen_y = int(
                self.padding + ((node.y - min_y) / range_y) * drawable_height
            )
            self.screen_coords[name] = (screen_x, screen_y)
