"""Composite cube-character rig. This layer owns geometry, not narrative intent."""

from __future__ import annotations

import numpy as np
from manim import AnimationGroup, BLACK, Cube, ManimColor, Mobject, OUT, RIGHT, UP, VGroup, smooth

from ...core.timing import positive_time
from .eye import CharacterEye
from .face import CharacterEyebrowPair, CharacterMouth

class BlockCharacter(VGroup):
    """A coloured cube with expressive eyes, eyebrows, and a mouth."""

    EYE_X_POSITIONS = (-0.32, 0.32)
    EYE_Y_POSITION = 0.25
    EYE_FACE_OFFSET = 0.005
    FACE_FEATURE_OFFSET = 0.014

    BODY_INDEX = 0
    EYES_INDEX = 1
    EYEBROWS_INDEX = 2
    MOUTH_INDEX = 3

    def __init__(
        self,
        colour: ManimColor,
        side_length: float = 2,
        *,
        eyes_open: bool = True,
        with_eyebrows: bool = True,
        with_mouth: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.colour = colour
        self.side_length = float(side_length)

        if self.side_length <= 0:
            raise ValueError("side_length must be greater than zero")

        body = self._create_body(
            colour,
            self.side_length,
        )
        eyes = self._create_eyes(
            colour,
            self.side_length,
            eyes_open=eyes_open,
        )
        face_depth = self.side_length / 2 + self.FACE_FEATURE_OFFSET
        eyebrows = (
            CharacterEyebrowPair(face_depth)
            if with_eyebrows
            else VGroup()
        )
        mouth = (
            CharacterMouth(face_depth)
            if with_mouth
            else VGroup()
        )

        # Fixed face slots preserve access when brows or mouth are disabled.
        self.add(body, eyes, eyebrows, mouth)

    @staticmethod
    def _create_body(
        colour: ManimColor,
        side_length: float,
    ) -> Cube:
        return Cube(
            side_length=side_length,
            fill_color=colour,
            fill_opacity=1,
            stroke_color=BLACK,
            stroke_width=2,
        )

    @classmethod
    def _create_eyes(
        cls,
        colour: ManimColor,
        side_length: float,
        *,
        eyes_open: bool,
    ) -> VGroup:
        eye_depth = side_length / 2 + cls.EYE_FACE_OFFSET

        return VGroup(
            *(
                CharacterEye(
                    pupil_colour=BLACK,
                    lid_colour=colour,
                    position=(
                        x_position * RIGHT
                        + cls.EYE_Y_POSITION * UP
                        + eye_depth * OUT
                    ),
                    eyes_open=eyes_open,
                )
                for x_position in cls.EYE_X_POSITIONS
            )
        )

    @property
    def body(self) -> Cube:
        return self[self.BODY_INDEX]

    @property
    def eyes(self) -> VGroup:
        return self[self.EYES_INDEX]

    @property
    def eyebrows(self) -> CharacterEyebrowPair:
        if not self.has_eyebrows:
            raise RuntimeError("This character has no eyebrows")
        return self[self.EYEBROWS_INDEX]

    @property
    def mouth(self) -> CharacterMouth:
        if not self.has_mouth:
            raise RuntimeError("This character has no mouth")
        return self[self.MOUTH_INDEX]

    @property
    def has_eyebrows(self) -> bool:
        return isinstance(self[self.EYEBROWS_INDEX], CharacterEyebrowPair)

    @property
    def has_mouth(self) -> bool:
        return isinstance(self[self.MOUTH_INDEX], CharacterMouth)

    @property
    def front_face(self) -> Mobject:
        # Cube face order: IN, OUT, LEFT, RIGHT, UP, DOWN.
        return self.body[1]

    @property
    def eyes_open(self) -> bool:
        return all(eye.eyes_open for eye in self.eyes)

    def get_face_basis(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.eyes[0].local_basis()

    def get_face_normal(self) -> np.ndarray:
        return self.get_face_basis()[2]

    def set_eyes_only_opacity(self, opacity: float) -> BlockCharacter:
        """Set only the eye opacity, leaving brows and mouth unchanged."""
        for eye in self.eyes:
            eye.set_opacity(opacity)
        return self

    def set_face_opacity(self, opacity: float) -> BlockCharacter:
        """Set camera-facing opacity for every facial feature."""
        self.set_eyes_only_opacity(opacity)
        if self.has_eyebrows:
            self.eyebrows.set_opacity(opacity)
        if self.has_mouth:
            self.mouth.set_opacity(opacity)
        return self

    def set_eye_opacity(self, opacity: float) -> BlockCharacter:
        """Historical hide-face helper retained for existing scene code."""
        return self.set_face_opacity(opacity)

    def set_lids(
        self,
        upper: float = 0.0,
        lower: float = 0.0,
    ) -> BlockCharacter:
        for eye in self.eyes:
            eye.set_lids(upper=upper, lower=lower)
        return self

    def lids_animation(
        self,
        upper: float = 0.0,
        lower: float = 0.0,
        run_time: float = 0.3,
        rate_func=smooth,
    ) -> AnimationGroup:
        run_time = positive_time(run_time)

        return AnimationGroup(
            *(
                eye.lids_animation(
                    upper=upper,
                    lower=lower,
                    run_time=run_time,
                    rate_func=rate_func,
                )
                for eye in self.eyes
            ),
            lag_ratio=0,
            run_time=run_time,
        )

    def set_eyes_open(self, eyes_open: bool) -> BlockCharacter:
        target = 0.0 if eyes_open else 1.0
        return self.set_lids(upper=target, lower=target)

    def open_eyes_animation(
        self,
        run_time: float = 0.3,
        rate_func=smooth,
    ) -> AnimationGroup:
        return self.lids_animation(
            upper=0.0,
            lower=0.0,
            run_time=run_time,
            rate_func=rate_func,
        )

    def close_eyes_animation(
        self,
        run_time: float = 0.3,
        rate_func=smooth,
    ) -> AnimationGroup:
        return self.lids_animation(
            upper=1.0,
            lower=1.0,
            run_time=run_time,
            rate_func=rate_func,
        )

    def look(
        self,
        x: float = 0,
        y: float = 0,
        run_time: float = 0.4,
    ) -> AnimationGroup:
        run_time = positive_time(run_time)

        return AnimationGroup(
            *(
                eye.pupil.animate.move_to(
                    eye.pupil_target(x=x, y=y)
                )
                for eye in self.eyes
            ),
            lag_ratio=0,
            run_time=run_time,
        )
__all__ = ["BlockCharacter"]
