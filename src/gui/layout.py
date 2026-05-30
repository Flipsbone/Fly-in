from src.algo.graph import Graph


class GraphLayout:
    """Calcul and store screen coordinates for a graph.

    The layout maps the graph node (x, y) coordinates into pixel
    positions inside a given window

    Attributes:
        graph: The graph to layout.
        padding: Pixels to leave as margin around the layout.
        screen_coords: Mapping of node name to (x, y) on screen.
    """

    def __init__(self, graph: Graph, padding: int) -> None:
        """Create a new layout for `graph` with `padding`.

        Args:
            graph: Graph instance containing nodes with `x` and `y`.
            padding: Margin in pixels to leave at window edges.
        """
        self.graph = graph
        self.padding = padding
        self.screen_coords: dict[str, tuple[int, int]] = {}

    def recalculate(self, window_width: int, window_height: int) -> None:
        """Rescales `screen_coords` for the current window size.

        This method rescales node coordinates to fit into the inner
        drawing area and stores integer pixel positions in
        `self.screen_coords`.

        Args:
            window_width: Width of the window in pixels.
            window_height: Height of the window in pixels.
        """
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
