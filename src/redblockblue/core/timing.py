"""Timing policy helpers.

Timing belongs above raw geometry: callers express duration/speed policy while
low-level rigs only receive a resolved run time.
"""

from __future__ import annotations

import numpy as np
from manim import Mobject


def positive_time(value: float, name: str = "duration") -> float:
    value = float(value)
    if not np.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and greater than zero")
    return value


def run_time_for_move(
    mobject: Mobject,
    target: np.ndarray,
    duration: float | None,
    speed: float | None,
    default_duration: float = 1.0,
) -> float:
    """Resolve either explicit duration or world-units-per-second speed."""
    if duration is not None and speed is not None:
        raise ValueError("Pass either duration or speed, not both")

    if speed is not None:
        speed = positive_time(speed, "speed")
        distance = np.linalg.norm(
            np.asarray(target, dtype=float) - mobject.get_center()
        )
        return max(float(distance / speed), 1 / 60)

    if duration is None:
        return positive_time(default_duration, "default_duration")
    return positive_time(duration)


__all__ = ["positive_time", "run_time_for_move"]
