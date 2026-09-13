"""Small geometry utilities shared by semantic animation domains."""

from __future__ import annotations

import numpy as np
from manim import OUT

EPSILON = 1e-8


def unit_vector(vector: np.ndarray, fallback: np.ndarray = OUT) -> np.ndarray:
    """Return a unit vector, using ``fallback`` for a degenerate input."""
    vector = np.asarray(vector, dtype=float)
    length = np.linalg.norm(vector)
    if length < EPSILON:
        return np.asarray(fallback, dtype=float).copy()
    return vector / length


__all__ = ["EPSILON", "unit_vector"]
