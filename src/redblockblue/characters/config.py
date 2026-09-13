"""Configuration defaults for RedBlockBlue cube characters."""

from __future__ import annotations

from manim import DEGREES, LEFT, OUT, RIGHT, UP, normalize

EYE_VISIBILITY_THRESHOLD = 0.25

RED_COLOUR = "#980000"
BLUE_COLOUR = "#0E76C6"

RED_START = LEFT * 2.3
BLUE_START = RIGHT * 2.3

INITIAL_Y_ROTATION = 20 * DEGREES
INITIAL_X_ROTATION = 8 * DEGREES

DIAGONAL_SPIN_AXIS = normalize(UP + RIGHT + 0.25 * OUT)

__all__ = [
    "EYE_VISIBILITY_THRESHOLD",
    "RED_COLOUR",
    "BLUE_COLOUR",
    "RED_START",
    "BLUE_START",
    "INITIAL_Y_ROTATION",
    "INITIAL_X_ROTATION",
    "DIAGONAL_SPIN_AXIS",
]
