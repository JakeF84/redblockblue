"""Renderer-conscious rigid-body motion primitives used by semantic controllers."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from manim import Mobject, TAU, UP, UpdateFromAlphaFunc, smooth

from .geometry import EPSILON, unit_vector
from .timing import positive_time

class _VerticalBounceUpdater:
    """Incremental bounce updater that does not pin a moving character in place."""

    def __init__(self, amplitude: float, period: float) -> None:
        self.amplitude = float(amplitude)
        self.period = positive_time(period, "period")
        self.elapsed_time = 0.0
        self.offset = 0.0

    def __call__(self, character: Mobject, dt: float) -> None:
        self.elapsed_time += dt
        next_offset = self.amplitude * np.sin(
            TAU * self.elapsed_time / self.period
        )
        character.shift((next_offset - self.offset) * UP)
        self.offset = float(next_offset)


def add_vertical_bounce(
    character: Mobject,
    amplitude: float = 0.22,
    period: float = 3.2,
) -> Callable[[Mobject, float], None]:
    """Attach a sinusoidal bounce and return the exact updater that was added.

    The updater applies only the change in bounce offset each frame. Unlike an
    updater that repeatedly calls ``move_to(home)``, it therefore preserves
    deliberate movement of the character.
    """
    updater = _VerticalBounceUpdater(amplitude, period)
    character.add_updater(updater)
    return updater


class _RigidMotion(UpdateFromAlphaFunc):
    """Resolve the starting pose when playback begins, including in a Succession."""

    def __init__(self, character, target, angle, axis, run_time, rate_func):
        self.target = np.asarray(target, dtype=float).copy()
        self.angle = float(angle)
        self.axis = unit_vector(axis, fallback=UP)
        self.previous_alpha = 0.0
        super().__init__(
            character, self._update_pose,
            run_time=positive_time(run_time), rate_func=rate_func,
            suspend_mobject_updating=True,
        )

    def begin(self):
        self.starting_centre = self.mobject.get_center().copy()
        self.displacement = self.target - self.starting_centre
        self.previous_alpha = 0.0
        super().begin()

    def _update_pose(self, mobject, alpha):
        delta_alpha = float(alpha) - self.previous_alpha
        if abs(delta_alpha) < EPSILON:
            return
        theta = self.angle * delta_alpha
        x, y, z = self.axis
        skew = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
        rotation = (
            np.cos(theta) * np.eye(3)
            + (1 - np.cos(theta)) * np.outer(self.axis, self.axis)
            + np.sin(theta) * skew
        )
        current_centre = self.starting_centre + self.displacement * self.previous_alpha
        mobject.apply_points_function_about_point(
            lambda points: points @ rotation.T + self.displacement * delta_alpha,
            about_point=current_centre,
        )
        self.previous_alpha = float(alpha)


def move_to_point(
    character: Mobject,
    target: np.ndarray,
    run_time: float = 1.0,
    rate_func=smooth,
) -> UpdateFromAlphaFunc:
    """Translate to a point, resolving the starting position at playback time."""
    return _RigidMotion(character, target, 0.0, UP, run_time, rate_func)


def move_and_spin(
    character: Mobject,
    target: np.ndarray,
    angle: float = TAU,
    axis: np.ndarray = UP,
    run_time: float = 4,
    rate_func=smooth,
) -> UpdateFromAlphaFunc:
    """Translate and rotate with one affine pass per frame.

    Automatic updaters pause during the move and resume when it finishes.
    """
    return _RigidMotion(character, target, angle, axis, run_time, rate_func)


__all__ = ["add_vertical_bounce", "move_to_point", "move_and_spin"]
