import arcade
from src.gui.visualizer import FlyInVisualizer


class VisualizerTestHelper(FlyInVisualizer):
    """
    Helper class to test Visualizer without initializing the Arcade window.
    This prevents OpenGL context crashes during headless CI testing.
    """
    def __init__(self) -> None:
        pass


def test_get_arcade_color_valid_colors() -> None:
    """Test that valid color strings return the correct arcade color tuple."""
    visu = VisualizerTestHelper()

    color_green = visu.get_arcade_color("green")
    color_red = visu.get_arcade_color("RED")

    assert color_green == arcade.color.GREEN
    assert color_red == arcade.color.RED


def test_get_arcade_color_none_or_invalid() -> None:
    """Test fallback colors for None or completely invalid color strings."""
    visu = VisualizerTestHelper()

    color_none = visu.get_arcade_color(None)
    color_invalid = visu.get_arcade_color("INVALID_COLOR")

    assert color_none == arcade.color.LIGHT_GRAY
    assert color_invalid == arcade.color.DARK_GRAY
