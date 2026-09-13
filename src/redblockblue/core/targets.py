"""One target model shared by characters and future semantic components."""

from __future__ import annotations

from typing import Any

import numpy as np
from manim import Mobject

TargetLike = Any


def resolve_target_source(target: TargetLike) -> Mobject | np.ndarray:
    """Resolve actor-like objects, Mobjects, or 2D/3D coordinates.

    Semantic objects can participate simply by exposing a ``mob`` property that
    is a Manim ``Mobject``. This deliberately avoids coupling core code to a
    particular actor implementation.
    """
    actor_mobject = getattr(target, "mob", None)
    if isinstance(actor_mobject, Mobject):
        return actor_mobject
    if isinstance(target, Mobject):
        return target

    point = np.asarray(target, dtype=float).reshape(-1)
    if point.size == 2:
        point = np.append(point, 0.0)
    if point.size != 3 or not np.all(np.isfinite(point)):
        raise ValueError("target must be actor-like, a Mobject, or a 2D/3D point")
    return point.copy()


def resolve_target_point(target: TargetLike) -> np.ndarray:
    source = resolve_target_source(target)
    if isinstance(source, Mobject):
        return np.asarray(source.get_center(), dtype=float)
    return np.asarray(source, dtype=float).copy()


__all__ = ["TargetLike", "resolve_target_source", "resolve_target_point"]
