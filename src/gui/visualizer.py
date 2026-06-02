import math
import arcade

from src.algo.graph import Graph
from src.gui.simulation import SimulationState
from src.gui.layout import GraphLayout
from src.gui.models_gui import HoveredNode


class FlyInVisualizer(arcade.Window):
    """Window that renders the graph and drone simulation.

    The visualizer uses `SimulationState` to know where drones are
    and `GraphLayout` to compute screen positions.
    """

    def __init__(
            self, graph: Graph, drone_paths: dict[int, list[str]]) -> None:
        """Create the visualizer window.

        Args:
            graph: Graph instance describing nodes and links.
            drone_paths: Mapping drone id -> list of locations for render.
        """

        super().__init__(
            1024, 768, "Fly-in: Drone Routing Visualizer", resizable=True
        )

        self.state = SimulationState(drone_paths)
        self.layout = GraphLayout(graph, 80)

        self.mouse_x: float = 0.0
        self.mouse_y: float = 0.0

        arcade.set_background_color(arcade.color.ALICE_BLUE)

    def setup(self) -> None:
        """Prepare layout and any needed resources before drawing."""
        self.layout.recalculate(self.width, self.height)

    def get_arcade_color(self, color_str: str | None) -> (
            tuple[int, int, int] | tuple[int, int, int, int]):
        """Return an `arcade.color` tuple for a color name.

        If `color_str` is None or unknown, return a default color.

        Args:
            color_str: The color name as a string.

        Returns:
            A tuple representing an RGB(A) color understood by Arcade.
        """
        if not color_str:
            return arcade.color.LIGHT_GRAY
        color_name: str = color_str.upper()
        return getattr(arcade.color, color_name, arcade.color.DARK_GRAY)

    def on_resize(self, width: int, height: int) -> None:
        """Handle window resize by updating the layout."""
        super().on_resize(width, height)
        self.setup()

    def on_mouse_motion(
            self, x: float, y: float, dx: float, dy: float) -> None:
        """Track mouse position used for hover tooltips."""
        self.mouse_x = x
        self.mouse_y = y

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle keyboard inputs for simulation navigation."""
        if key == arcade.key.RIGHT:
            self.state.next_turn()
        elif key == arcade.key.LEFT:
            self.state.previous_turn()
        elif key == arcade.key.ESCAPE:
            arcade.exit()

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear()

        positions = self.state.get_drones_positions()
        hovered_link_text = self._draw_connections(positions.on_links)
        hovered_node = self._draw_nodes(positions.on_nodes)

        if hovered_node:
            node_text = (
                f"hub: {hovered_node.name}\nzone_type: {hovered_node.type}")
            self._draw_tooltip(node_text)
        elif hovered_link_text:
            self._draw_tooltip(hovered_link_text)

        self._draw_ui()

    def _draw_single_link(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> None:
        """Draw a single line between two coordinates."""
        arcade.draw_line(start_x, start_y, end_x, end_y, arcade.color.GRAY, 2)

    def _draw_drones_circle(
        self, start_x: int,
        start_y: int, end_x: int,
        end_y: int, drones: list[int]
    ) -> None:

        """Draw a circle with drone ids for drones on a link."""
        mid_x = (start_x + end_x) // 2
        mid_y = (start_y + end_y) // 2
        text: str = ", ".join(f"D{d}" for d in drones)

        arcade.draw_circle_filled(mid_x, mid_y, 14, arcade.color.YELLOW)
        arcade.draw_circle_outline(mid_x, mid_y, 14, arcade.color.BLACK, 1)

        arcade.Text(
            text=text,
            x=mid_x,
            y=mid_y,
            color=arcade.color.BLACK,
            font_size=10,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        ).draw()

    def _is_mouse_on_link(
            self, start_x: int, start_y: int, end_x: int, end_y: int) -> bool:
        """Roughly check if the mouse is hovering over a line segment.

        Args:
            start_x (int): The x-coordinate of the starting node.
            start_y (int): The y-coordinate of the starting node.
            end_x (int): The x-coordinate of the ending node.
            end_y (int): The y-coordinate of the ending node.
            self.mouse_x (float): The current x-coordinate of the mouse.
            self.mouse_y (float): The current y-coordinate of the mouse.
        Returns:
            bool: True if the mouse is within the collision tolerance,
            False otherwise.
        """

        dist_to_start = math.hypot(
            self.mouse_x - start_x, self.mouse_y - start_y)
        dist_to_end = math.hypot(self.mouse_x - end_x, self.mouse_y - end_y)
        line_length = math.hypot(end_x - start_x, end_y - start_y)

        return (dist_to_start + dist_to_end) <= (line_length + 1.5)

    def _draw_connections(
            self, drones_on_links: dict[tuple[str, str],
                                        list[int]]) -> str | None:
        """Draw all graph links and return hovered link tooltip text if any.

         Args:
            drones_on_links : tuple of node names -> list of drone ids on that
            link for current turn.
        Returns:
            str | None: Tooltip text for the hovered link, or None if no link
            is hovered.
            """
        drawn_links: set[tuple[str, str]] = set()
        hovered_link_text: str | None = None

        for node in self.layout.graph.nodes.values():
            start_x, start_y = self.layout.screen_coords[node.name]

            for neighbor_name in node.neighbors:
                link_id: tuple[str, str] = (
                    min(node.name, neighbor_name),
                    max(node.name, neighbor_name)
                )

                if link_id in drawn_links:
                    continue

                end_x, end_y = self.layout.screen_coords[neighbor_name]
                self._draw_single_link(start_x, start_y, end_x, end_y)

                if link_id in drones_on_links:
                    self._draw_drones_circle(
                        start_x, start_y,
                        end_x, end_y, drones_on_links[link_id]
                    )
                if self._is_mouse_on_link(start_x, start_y, end_x, end_y):
                    hovered_link_text = (
                        f"capacity: {node.neighbors[neighbor_name]}")

                drawn_links.add(link_id)

        return hovered_link_text

    def _draw_nodes(
        self, drones_on_nodes: dict[str, int]
    ) -> HoveredNode | None:
        """Draw nodes and return hovered node information if any.

        Args:
            drones_on_nodes: Mapping of node names to the count
                of drones on that node for the current turn.

        Returns:
            HoveredNode | None: Information about the hovered node, or None if
            no node is hovered.
        """
        hovered_node: HoveredNode | None = None

        for node in self.layout.graph.nodes.values():
            screen_x, screen_y = self.layout.screen_coords[node.name]
            node_color = self.get_arcade_color(node.zone_color)

            arcade.draw_circle_filled(screen_x, screen_y, 20, node_color)

            if node.name in drones_on_nodes:
                count: int = drones_on_nodes[node.name]

                arcade.Text(
                    text=str(count),
                    x=screen_x,
                    y=screen_y,
                    color=arcade.color.WHITE,
                    font_size=14,
                    anchor_x="center",
                    anchor_y="center",
                    bold=True,
                ).draw()

            distance: float = math.hypot(
                self.mouse_x - screen_x, self.mouse_y - screen_y
            )
            if distance <= 20.0:
                hovered_node = HoveredNode(
                    name=node.name,
                    type=node.zone_type,
                    x=screen_x,
                    y=screen_y)

        return hovered_node

    def _draw_tooltip(self, text: str) -> None:
        """Draw a small tooltip box for the provided text."""
        lines = text.split('\n')
        max_length = max(len(line) for line in lines)

        box_width: int = max(120, max_length * 10)
        box_height: int = 20 * len(lines) + 20

        margin: float = 20.0
        center_x: float = self.width - (box_width / 2.0) - margin
        center_y: float = self.height - (box_height / 2.0) - margin
        half_w: float = box_width / 2.0
        half_h: float = box_height / 2.0

        box_points = (
            (center_x - half_w, center_y - half_h),
            (center_x + half_w, center_y - half_h),
            (center_x + half_w, center_y + half_h),
            (center_x - half_w, center_y + half_h),
        )

        arcade.draw_polygon_filled(box_points, arcade.color.WHITE)
        arcade.draw_polygon_outline(box_points, arcade.color.BLACK, 1)

        arcade.Text(
            text=text,
            x=center_x,
            y=center_y,
            color=arcade.color.BLACK,
            font_size=12,
            anchor_x="center",
            anchor_y="center",
            align="center",
            multiline=True,
            bold=True,
            width=int(box_width),
        ).draw()

    def _draw_ui(self) -> None:
        """Draw simple UI text such as the current turn."""
        arcade.Text(
            text=f"Turn: {self.state.current_turn} / {self.state.max_turn}",
            x=20,
            y=self.height - 30,
            color=arcade.color.BLACK,
            font_size=16,
            bold=True,
        ).draw()

        arcade.Text(
            text="Use left and right arrows to navigate",
            x=20,
            y=self.height - 50,
            color=arcade.color.DARK_GRAY,
            font_size=12,
        ).draw()
