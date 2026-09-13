"""Whole-character movement. Scene-level intent is kept separate from rig geometry."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy as np
from manim import Mobject, Rotate, TAU, UP, smooth

from ...core.motion import add_vertical_bounce, move_and_spin, move_to_point
from ...core.targets import TargetLike, resolve_target_point
from ...core.timing import positive_time, run_time_for_move

if TYPE_CHECKING:
    from ..actor import CharacterActor


class CharacterMotion:
    DEFAULT_MOVE_DURATION = 1.0
    DEFAULT_SPIN_DURATION = 1.0

    def __init__(self, actor: CharacterActor) -> None:
        self.actor = actor
        self.scene = actor.scene
        self.character = actor.character
        self._bounce_updater: Callable[[Mobject, float], None] | None = None

    def move_animation(
        self,
        target: TargetLike,
        duration: float | None = None,
        *,
        speed: float | None = None,
        rate_func=smooth,
    ):
        target_point = resolve_target_point(target)
        run_time = run_time_for_move(
            self.character, target_point, duration, speed,
            default_duration=self.DEFAULT_MOVE_DURATION,
        )
        return move_to_point(
            self.character, target_point, run_time=run_time, rate_func=rate_func
        )

    def move_to(self, target: TargetLike, duration: float | None = None, *, speed: float | None = None, rate_func=smooth) -> CharacterMotion:
        self.scene.play(self.move_animation(target, duration, speed=speed, rate_func=rate_func))
        return self

    def move_and_spin_animation(
        self,
        target: TargetLike,
        duration: float | None = None,
        *,
        speed: float | None = None,
        turns: float = 1.0,
        axis: np.ndarray = UP,
        rate_func=smooth,
    ):
        target_point = resolve_target_point(target)
        run_time = run_time_for_move(
            self.character, target_point, duration, speed,
            default_duration=self.DEFAULT_MOVE_DURATION,
        )
        return move_and_spin(
            self.character,
            target=target_point,
            angle=float(turns) * TAU,
            axis=axis,
            run_time=run_time,
            rate_func=rate_func,
        )

    def move_and_spin(self, target: TargetLike, duration: float | None = None, **kwargs) -> CharacterMotion:
        self.scene.play(self.move_and_spin_animation(target, duration, **kwargs))
        return self

    def spin_animation(
        self,
        turns: float = 1.0,
        duration: float = DEFAULT_SPIN_DURATION,
        *,
        axis: np.ndarray = UP,
        rate_func=smooth,
    ) -> Rotate:
        return Rotate(
            self.character,
            angle=float(turns) * TAU,
            axis=axis,
            about_point=self.character.get_center(),
            run_time=positive_time(duration),
            rate_func=rate_func,
        )

    def spin(self, turns: float = 1.0, duration: float = DEFAULT_SPIN_DURATION, **kwargs) -> CharacterMotion:
        self.scene.play(self.spin_animation(turns, duration, **kwargs))
        return self

    def bounce(self, amplitude: float = 0.22, period: float = 3.2) -> CharacterMotion:
        self.stop_bounce()
        self._bounce_updater = add_vertical_bounce(
            self.character, amplitude=amplitude, period=period
        )
        return self

    def stop_bounce(self) -> CharacterMotion:
        if self._bounce_updater is not None:
            self.character.remove_updater(self._bounce_updater)
            self._bounce_updater = None
        return self


__all__ = ["CharacterMotion"]
