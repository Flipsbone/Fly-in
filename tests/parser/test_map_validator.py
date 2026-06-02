"""Unit tests for the Pydantic models edge cases (map_validator.py)."""

import pytest
from pydantic import ValidationError
from src.parser.map_validator import (
    Zone_Approval, Connection_Approval, Drone_Approval)


def test_drone_approval_zero_or_negative() -> None:
    """Test edge case: Number of drones must be strictly positive."""
    with pytest.raises(ValidationError):
        Drone_Approval(nb_drones=0)
    with pytest.raises(ValidationError):
        Drone_Approval(nb_drones=-5)


def test_zone_name_with_multiple_dashes() -> None:
    """Test edge case: Zone names with any dash should be rejected."""
    raw_data = {"name": "zone-a-b", "x": 1, "y": 2, "line": 10}
    with pytest.raises(ValidationError) as exc:
        Zone_Approval.model_validate(raw_data)
    assert "zone names cannot contain dashes" in str(exc.value)


def test_zone_metadata_malformed_brackets() -> None:
    """Test edge case: Metadata with unclosed or nested brackets."""
    invalid_metadatas = [
        "[color=red",         # Unclosed
        "color=red]",         # Unopened
        "[[color=red]]",      # Nested
        "[color=red] extra",  # Content outside
    ]
    for meta in invalid_metadatas:
        raw_data = {"name": "z1", "x": 0, "y": 0, "metadata": meta, "line": 1}
        with pytest.raises(ValidationError):
            Zone_Approval.model_validate(raw_data)


def test_zone_metadata_duplicate_keys() -> None:
    """Test edge case: Same metadata key defined twice."""
    raw_data = {
        "name": "z1",
        "x": 0,
        "y": 0,
        "metadata": "[color=red color=blue]",
        "line": 1
    }
    with pytest.raises(ValidationError) as exc:
        Zone_Approval.model_validate(raw_data)
    assert "cant be present twice" in str(exc.value)


def test_zone_metadata_invalid_zone_type() -> None:
    """Test edge case: Zone type not in allowed list."""
    raw_data = {
        "name": "z1",
        "x": 0,
        "y": 0,
        "metadata": "[zone=magic]",
        "line": 1
    }
    with pytest.raises(ValidationError) as exc:
        Zone_Approval.model_validate(raw_data)
    assert "Unknown metadata value" in str(exc.value)


def test_connection_self_loop() -> None:
    """Test edge case: A zone connecting to itself is invalid."""
    raw_data = {"link_1": "hubA", "link_2": "hubA"}
    with pytest.raises(ValidationError) as exc:
        Connection_Approval.model_validate(raw_data)
    assert "link cannot connect to itself" in str(exc.value)


def test_connection_capacity_zero() -> None:
    """Test edge case: Link capacity must be >= 0."""
    raw_data = {
        "link_1": "hubA",
        "link_2": "hubB",
        "metadata": "[max_link_capacity=-1]"
    }
    with pytest.raises(ValidationError) as exc:
        Connection_Approval.model_validate(raw_data)
    assert "must be an integer >= 0" in str(exc.value)
