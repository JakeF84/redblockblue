"""Project scene base and semantic object factories."""

from __future__ import annotations

import numpy as np
from manim import ManimColor, ORIGIN, ThreeDScene

from .characters.actor import CharacterActor
from .characters.config import (
    BLUE_COLOUR, INITIAL_X_ROTATION, INITIAL_Y_ROTATION, RED_COLOUR,
)
from .characters.rig import BlockCharacter, EyeVisibilityController


class RBBScene(ThreeDScene):
    """ThreeDScene with RedBlockBlue semantic character factories."""

    def _get_visibility_controller(self) -> EyeVisibilityController:
        controller = getattr(self, "_rbb_character_visibility_controller", None)
        if controller is None:
            controller = EyeVisibilityController(scene=self)
            self._rbb_character_visibility_controller = controller
            self.add(controller)
        return controller

    def character(
        self,
        colour: ManimColor,
        at: np.ndarray = ORIGIN,
        *,
        side_length: float = 2,
        y_rotation: float = INITIAL_Y_ROTATION,
        x_rotation: float = INITIAL_X_ROTATION,
        eyes_open: bool = True,
        with_eyebrows: bool = True,
        with_mouth: bool = True,
    ) -> CharacterActor:
        character = BlockCharacter(
            colour,
            side_length=side_length,
            eyes_open=eyes_open,
            with_eyebrows=with_eyebrows,
            with_mouth=with_mouth,
        ).move_to(at)
        character.rotate(y_rotation, axis=np.array([0.0, 1.0, 0.0]))
        character.rotate(x_rotation, axis=np.array([1.0, 0.0, 0.0]))

        visibility = self._get_visibility_controller()
        visibility.add_character(character)
        self.add(character)
        character.update(0)
        visibility.refresh()
        return CharacterActor(self, character, visibility)

    def red(self, at: np.ndarray = ORIGIN, **kwargs) -> CharacterActor:
        return self.character(RED_COLOUR, at=at, **kwargs)

    def blue(self, at: np.ndarray = ORIGIN, **kwargs) -> CharacterActor:
        return self.character(BLUE_COLOUR, at=at, **kwargs)

    def together(self, *animations) -> None:
        """Concise DSL helper for simultaneous semantic animations."""
        self.play(*animations)


# Historical name retained for existing scenes.
CharacterScene = RBBScene

__all__ = ["RBBScene", "CharacterScene"]
