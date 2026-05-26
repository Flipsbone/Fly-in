"""Unit tests for the Pathfinding logic edge cases."""

from unittest.mock import MagicMock
from src.algo.pathfinding import PathFinder
from src.algo.graph import Graph
from src.algo.reservation_table import ReservationTable
from src.algo.node import Node


def test_pathfinding_no_possible_path() -> None:
    """Test edge case: The end node is completely isolated/disconnected."""
    mock_graph = MagicMock(spec=Graph)
    mock_graph.start_name = "start"
    mock_graph.end_name = "end"

    node_start = MagicMock(spec=Node)
    node_start.neighbors = {}  # No neighbors! Isolated.
    node_start.zone_type = "normal"

    node_end = MagicMock(spec=Node)
    node_end.neighbors = {}
    node_end.zone_type = "normal"

    mock_graph.nodes = {"start": node_start, "end": node_end}
    mock_reservation = MagicMock(spec=ReservationTable)

    pathfinder = PathFinder(graph=mock_graph, reservation=mock_reservation)

    assert pathfinder.is_one_solution() is False


def test_pathfinding_all_paths_blocked() -> None:
    """Test edge case: Path exists structurally,
    but is blocked by zone rules."""
    mock_graph = MagicMock(spec=Graph)
    mock_graph.start_name = "start"
    mock_graph.end_name = "end"

    node_start = MagicMock(spec=Node)
    node_start.neighbors = {"wall": 1}
    node_start.zone_type = "normal"

    node_wall = MagicMock(spec=Node)
    node_wall.neighbors = {"start": 1, "end": 1}
    node_wall.zone_type = "blocked"  # Completely impassable

    node_end = MagicMock(spec=Node)
    node_end.neighbors = {"wall": 1}
    node_end.zone_type = "normal"

    mock_graph.nodes = {
        "start": node_start,
        "wall": node_wall,
        "end": node_end
    }
    mock_reservation = MagicMock(spec=ReservationTable)

    pathfinder = PathFinder(graph=mock_graph, reservation=mock_reservation)

    assert pathfinder.is_one_solution() is False
