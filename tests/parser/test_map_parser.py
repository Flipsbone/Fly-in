"""Unit tests for the MapParser state machine and logic (map_parser.py)."""

import pytest
from pathlib import Path
from src.parser.map_parser import MapParser


def test_parser_missing_start_or_end(tmp_path: Path) -> None:
    """Test edge case: Map without start_hub or without end_hub."""
    map_content = (
        "nb_drones: 5\n"
        "hub: my_hub 0 0\n"
        "end_hub: end 10 10\n"  # Missing start_hub
    )
    test_file = tmp_path / "missing_start.txt"
    test_file.write_text(map_content)

    parser = MapParser()
    with open(test_file, 'r', encoding="utf-8") as f:
        with pytest.raises(ValueError) as exc:
            parser.parse_map(f)
        assert "Missing start_hub" in str(exc.value)


def test_parser_duplicate_coordinates(tmp_path: Path) -> None:
    """Test edge case: Two hubs sharing the exact same (x, y) coordinates."""
    map_content = (
        "nb_drones: 5\n"
        "start_hub: start 0 0\n"
        "hub: overlap 0 0\n"  # Duplicate coords!
        "end_hub: end 10 10\n"
    )
    test_file = tmp_path / "dup_coords.txt"
    test_file.write_text(map_content)

    parser = MapParser()
    with open(test_file, 'r', encoding="utf-8") as f:
        with pytest.raises(ValueError) as exc:
            parser.parse_map(f)
        assert "Duplicate coordinates" in str(exc.value)


def test_parser_connection_to_unknown_zone(tmp_path: Path) -> None:
    """Test edge case: Connection referencing a zone that wasn't declared."""
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0\n"
        "end_hub: end 10 10\n"
        "connection: start-ghost_hub\n"  # ghost_hub does not exist
    )
    test_file = tmp_path / "ghost_connection.txt"
    test_file.write_text(map_content)

    parser = MapParser()
    with open(test_file, 'r', encoding="utf-8") as f:
        with pytest.raises(ValueError) as exc:
            parser.parse_map(f)
        assert "previously defined zones" in str(exc.value)


def test_parser_duplicate_connections(tmp_path: Path) -> None:
    """Test edge case: Declaring a connection twice, even inverted."""
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0\n"
        "end_hub: end 10 10\n"
        "connection: start-end\n"
        "connection: end-start\n"  # Inverted duplicate
    )
    test_file = tmp_path / "dup_connections.txt"
    test_file.write_text(map_content)

    parser = MapParser()
    with open(test_file, 'r', encoding="utf-8") as f:
        with pytest.raises(ValueError) as exc:
            parser.parse_map(f)
        assert "Duplicate connection" in str(exc.value)
