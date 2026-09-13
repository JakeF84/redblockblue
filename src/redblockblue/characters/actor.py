"""Narrative-facing character actor.

The actor is deliberately small. Raw geometry is in ``rig``; primitive facial
controls are namespaced; whole-body motion are capability objects.
Only high-value narrative verbs are promoted onto the actor itself.
"""

from __future__ import annotations

import numpy as np
from manim import ThreeDScene, UP, smooth

from ..core.targets import TargetLike
from ._legacy import LegacyActorAPI
from .controls.eyes import CharacterEyes
from .controls.expressions import CharacterExpressions
from .controls.face import CharacterEyebrows, CharacterMouthController
from .controls.motion import CharacterMotion
from .rig import BlockCharacter, EyeVisibilityController


class CharacterActor(LegacyActorAPI):
    """Semantic controller around one ``BlockCharacter`` rig."""

    def __init__(
        self,
        scene: ThreeDScene,
        character: BlockCharacter,
        visibility_controller: EyeVisibilityController | None = None,
    ) -> None:
        self.scene = scene
        self.character = character
        self.visibility_controller = visibility_controller
        self._eyes = CharacterEyes(scene, character)
        self._eyebrows = CharacterEyebrows(scene, character)
        self._mouth = CharacterMouthController(scene, character)
        self._motion = CharacterMotion(self)
        self._expressions = CharacterExpressions(self)

    @property
    def mob(self) -> BlockCharacter:
        return self.character

    @property
    def eyes(self) -> CharacterEyes:
        return self._eyes

    @property
    def eyebrows(self) -> CharacterEyebrows:
        return self._eyebrows

    @property
    def mouth(self) -> CharacterMouthController:
        return self._mouth

    @property
    def expressions(self) -> CharacterExpressions:
        return self._expressions

    @property
    def motion(self) -> CharacterMotion:
        return self._motion

    def wait(self, duration: float = 1.0) -> CharacterActor:
        self.scene.wait(duration)
        return self

    # Narrative gaze -----------------------------------------------------
    def look_at_animation(self, target: TargetLike, duration: float = 0.4, *, amount: float = 0.06):
        return self.eyes.look_at_animation(target, duration, amount=amount)

    def look_at(self, target: TargetLike, duration: float = 0.4, *, amount: float = 0.06) -> CharacterActor:
        self.eyes.look_at(target, duration, amount=amount)
        return self

    def track(self, target: TargetLike, *, amount: float = 0.06) -> CharacterActor:
        self.eyes.track(target, amount=amount)
        return self

    def stop_tracking(self) -> CharacterActor:
        self.eyes.stop_tracking()
        return self

    # Narrative expression ----------------------------------------------
    def react_animation(self, expression: str, duration: float = 0.4, *, rate_func=smooth):
        return self.expressions.animation(expression, duration, rate_func=rate_func)

    def react(self, expression: str, duration: float = 0.4, *, rate_func=smooth) -> CharacterActor:
        self.expressions.apply(expression, duration, rate_func=rate_func)
        return self

    # Narrative movement -------------------------------------------------
    def move_animation(self, target: TargetLike, duration: float | None = None, **kwargs):
        return self.motion.move_animation(target, duration, **kwargs)

    def move_to(self, target: TargetLike, duration: float | None = None, **kwargs) -> CharacterActor:
        self.motion.move_to(target, duration, **kwargs)
        return self

    def move_and_spin_animation(self, target: TargetLike, duration: float | None = None, **kwargs):
        return self.motion.move_and_spin_animation(target, duration, **kwargs)

    def move_and_spin(self, target: TargetLike, duration: float | None = None, **kwargs) -> CharacterActor:
        self.motion.move_and_spin(target, duration, **kwargs)
        return self

    def spin_animation(self, turns: float = 1.0, duration: float = 1.0, *, axis: np.ndarray = UP, rate_func=smooth):
        return self.motion.spin_animation(turns, duration, axis=axis, rate_func=rate_func)

    def spin(self, turns: float = 1.0, duration: float = 1.0, **kwargs) -> CharacterActor:
        self.motion.spin(turns, duration, **kwargs)
        return self

    def bounce(self, amplitude: float = 0.22, period: float = 3.2) -> CharacterActor:
        self.motion.bounce(amplitude, period)
        return self

    def stop_bounce(self) -> CharacterActor:
        self.motion.stop_bounce()
        return self


__all__ = ["CharacterActor"]
