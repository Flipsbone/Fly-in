import pytest
import io
from src.parser.map_parser import parse_map


def test_parse_valid_simple_map():
    # 1. Setup (Arrange): We simulate a valid file
    valid_map_content = """
    nb_drones: 5
    start_hub: base 0 0 [color=green max_drones=5]
    end_hub: destination 10 10 [max_drones=5]
    hub: relais 5 5 [zone=priority]
    connection: base-relais
    connection: relais-destination
    """
    fake_file = io.StringIO(valid_map_content)

    # 2. Execution (Act)
    network = parse_map(fake_file)

    # 3. Verification (Assert)
    assert network.nb_drones == 5
    assert network.start_node is not None
    assert network.start_node.name == "base"
    assert "relais" in network.zones
    assert network.zones["relais"].zone == "priority"
    assert len(network.connections) == 2


def test_parse_invalid_drone_number():
    # We test that the parser properly raises a ValueError
    # if nb_drones is invalid
    invalid_content = """
    nb_drones: -2
    start_hub: base 0 0 [max_drones=5]
    end_hub: dest 10 10 [max_drones=5]
    """
    fake_file = io.StringIO(invalid_content)

    with pytest.raises(ValueError, match="must be integer > 0"):
        parse_map(fake_file)


def test_parse_duplicate_coordinates():
    # We test the rejection of duplicate coordinates
    duplicate_coords_content = """
    nb_drones: 2
    start_hub: base 0 0 [max_drones=2]
    end_hub: dest 0 0 [max_drones=2]
    """
    fake_file = io.StringIO(duplicate_coords_content)

    # The match parameter allows us to verify that a part of
    # the error message matches
    with pytest.raises(ValueError, match="Duplicate coordinates"):
        parse_map(fake_file)
