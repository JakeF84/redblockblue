"""Camera-facing visibility policy for facial features."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from manim import Mobject, OUT, ThreeDScene

from ...core.geometry import unit_vector
from ..config import EYE_VISIBILITY_THRESHOLD
from .character import BlockCharacter

class EyeVisibilityController(Mobject):
    """Keep face-feature visibility aligned with the camera."""

    def __init__(
        self,
        scene: ThreeDScene,
        characters: Iterable[BlockCharacter] = (),
        threshold: float = EYE_VISIBILITY_THRESHOLD,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.scene = scene
        self.characters: list[BlockCharacter] = []
        self.threshold = float(threshold)

        for character in characters:
            self.add_character(character)

        self.add_updater(self._refresh)

    def add_character(
        self,
        character: BlockCharacter,
    ) -> EyeVisibilityController:
        if not any(
            existing is character
            for existing in self.characters
        ):
            self.characters.append(character)

        return self

    def remove_character(
        self,
        character: BlockCharacter,
    ) -> EyeVisibilityController:
        self.characters = [
            existing
            for existing in self.characters
            if existing is not character
        ]
        return self

    def camera_direction(self) -> np.ndarray:
        direction = (
            self.scene.camera.get_rotation_matrix().T @ OUT
        )
        return unit_vector(direction, fallback=OUT)

    def update_character(
        self,
        character: BlockCharacter,
        camera_direction: np.ndarray | None = None,
    ) -> None:
        if camera_direction is None:
            camera_direction = self.camera_direction()

        facing_amount = float(
            np.dot(
                character.get_face_normal(),
                camera_direction,
            )
        )

        character.set_face_opacity(
            1.0
            if facing_amount > self.threshold
            else 0.0
        )

    def refresh(self) -> None:
        camera_direction = self.camera_direction()

        for character in self.characters:
            self.update_character(
                character,
                camera_direction,
            )

    def _refresh(
        self,
        _controller: Mobject,
    ) -> None:
        self.refresh()
__all__ = ["EyeVisibilityController"]
