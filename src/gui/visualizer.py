import math
import arcade

from src.algo.graph import Graph
from src.gui.simulation import SimulationState
from src.gui.layout import GraphLayout


class FlyInVisualizer(arcade.Window):

    def __init__(
            self, graph: Graph, drone_paths: dict[int, list[str]]) -> None:

        super().__init__(
            1024, 768, "Fly-in: Drone Routing Visualizer", resizable=True
        )

        self.state = SimulationState(drone_paths)
        self.layout = GraphLayout(graph)

        self.mouse_x: float = 0.0
        self.mouse_y: float = 0.0

        arcade.set_background_color(arcade.color.ALICE_BLUE)

    def setup(self) -> None:
        self.layout.recalculate(self.width, self.height)

    def get_arcade_color(self, color_str: str | None) -> (
            tuple[int, int, int] | tuple[int, int, int, int]):
        if not color_str:
            return arcade.color.LIGHT_GRAY
        color_name: str = color_str.upper()
        return getattr(arcade.color, color_name, arcade.color.DARK_GRAY)

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.setup()

    def on_mouse_motion(
            self, x: float, y: float, dx: float, dy: float) -> None:

        self.mouse_x = x
        self.mouse_y = y

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.RIGHT:
            self.state.next_turn()
        elif key == arcade.key.LEFT:
            self.state.previous_turn()

    def on_draw(self) -> None:
        self.clear()

        nodes_drones, links_drones = self.state.get_drones_positions()

        self._draw_connections(links_drones)
        hovered_node = self._draw_nodes(nodes_drones)

        if hovered_node:
            self._draw_tooltip(hovered_node)

        self._draw_ui()

    def _draw_connections(
        self, drones_on_links: dict[tuple[str, str], list[int]]
    ) -> None:
        drawn_links: set[tuple[str, str]] = set()

        for node in self.layout.graph.nodes.values():
            if node.name not in self.layout.screen_coords:
                continue

            start_x, start_y = self.layout.screen_coords[node.name]

            for neighbor_name in node.neighbors:
                if neighbor_name not in self.layout.screen_coords:
                    continue

                link_id: tuple[str, str] = (
                    min(node.name, neighbor_name),
                    max(node.name, neighbor_name))

                if link_id in drawn_links:
                    continue

                end_x, end_y = self.layout.screen_coords[neighbor_name]

                arcade.draw_line(
                    start_x, start_y, end_x, end_y, arcade.color.GRAY, 2
                )

                if link_id in drones_on_links:
                    drones = drones_on_links[link_id]
                    text: str = ", ".join(f"D{d}" for d in drones)

                    mid_x = (start_x + end_x) // 2
                    mid_y = (start_y + end_y) // 2

                    arcade.draw_circle_filled(
                        mid_x, mid_y, 14, arcade.color.YELLOW
                    )
                    arcade.draw_circle_outline(
                        mid_x, mid_y, 14, arcade.color.BLACK, 1
                    )

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

                drawn_links.add(link_id)

    def _draw_nodes(
        self, drones_on_nodes: dict[str, int]
    ) -> tuple[str, int, int] | None:
        hovered_node: tuple[str, int, int] | None = None

        for node in self.layout.graph.nodes.values():
            if node.name not in self.layout.screen_coords:
                continue

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
                hovered_node = (node.name, screen_x, screen_y)

        return hovered_node

    def _draw_tooltip(self, hovered_node: tuple[str, int, int]) -> None:
        name, sx, sy = hovered_node

        box_width: int = len(name) * 10
        box_height: int = 24

        center_x: float = float(sx)
        center_y: float = sy + 35.0
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
            text=name,
            x=sx,
            y=sy + 30,
            color=arcade.color.BLACK,
            font_size=12,
            anchor_x="center",
            bold=True,
        ).draw()

    def _draw_ui(self) -> None:
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
