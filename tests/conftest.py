import pytest
from manim import tempconfig


@pytest.fixture(autouse=True)
def manim_config(tmp_path):
    with tempconfig({
        "media_dir": str(tmp_path), "dry_run": True,
        "disable_caching": True, "quality": "low_quality",
        "pixel_width": 320, "pixel_height": 180, "frame_rate": 10,
        "verbosity": "ERROR", "progress_bar": "none",
    }):
        yield
