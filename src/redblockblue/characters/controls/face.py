"""Semantic facial primitive controls. Geometry lives in ``characters.rig``."""

from __future__ import annotations

from typing import Literal
import numpy as np
from manim import ThreeDScene, UpdateFromAlphaFunc, smooth

from ..rig.character import BlockCharacter
from ..rig.face import CharacterEyebrowPair, CharacterMouth

BrowSide = Literal["left", "right"]

class CharacterEyebrows:
    """High-level eyebrow controller exposed as ``actor.eyebrows``."""

    DEFAULT_DURATION = 0.3
    DEFAULT_RAISE = 0.12
    DEFAULT_LOWER = -0.08
    DEFAULT_FURROW_ANGLE = 16 * np.pi / 180
    DEFAULT_WORRIED_ANGLE = 14 * np.pi / 180

    def __init__(self, scene: ThreeDScene, character: BlockCharacter) -> None:
        self.scene = scene
        self.character = character

    @property
    def mob(self) -> CharacterEyebrowPair:
        if not self.character.has_eyebrows:
            raise RuntimeError("This character has no eyebrows")
        return self.character.eyebrows

    def pose_animation(
        self,
        *,
        left_height: float = 0.0,
        right_height: float = 0.0,
        left_angle: float = 0.0,
        right_angle: float = 0.0,
        duration: float = DEFAULT_DURATION,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.mob.pose_animation(
            left_height=left_height,
            right_height=right_height,
            left_angle=left_angle,
            right_angle=right_angle,
            run_time=duration,
            rate_func=rate_func,
        )

    def pose(self, **kwargs) -> CharacterEyebrows:
        self.scene.play(self.pose_animation(**kwargs))
        return self

    move_animation = pose_animation
    move = pose

    def neutral_animation(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.pose_animation(duration=duration, rate_func=rate_func)

    def neutral(self, duration: float = DEFAULT_DURATION, *, rate_func=smooth) -> CharacterEyebrows:
        self.scene.play(self.neutral_animation(duration, rate_func=rate_func))
        return self

    def raise_animation(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_RAISE,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.pose_animation(
            left_height=amount,
            right_height=amount,
            duration=duration,
            rate_func=rate_func,
        )

    def raise_(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_RAISE,
        rate_func=smooth,
    ) -> CharacterEyebrows:
        self.scene.play(
            self.raise_animation(duration, amount=amount, rate_func=rate_func)
        )
        return self

    def lower_animation(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_LOWER,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.pose_animation(
            left_height=amount,
            right_height=amount,
            duration=duration,
            rate_func=rate_func,
        )

    def lower(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_LOWER,
        rate_func=smooth,
    ) -> CharacterEyebrows:
        self.scene.play(
            self.lower_animation(duration, amount=amount, rate_func=rate_func)
        )
        return self

    def furrow_animation(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        angle: float = DEFAULT_FURROW_ANGLE,
        height: float = -0.04,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.pose_animation(
            left_height=height,
            right_height=height,
            left_angle=-abs(angle),
            right_angle=abs(angle),
            duration=duration,
            rate_func=rate_func,
        )

    def furrow(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        angle: float = DEFAULT_FURROW_ANGLE,
        height: float = -0.04,
        rate_func=smooth,
    ) -> CharacterEyebrows:
        self.scene.play(
            self.furrow_animation(
                duration,
                angle=angle,
                height=height,
                rate_func=rate_func,
            )
        )
        return self

    def worried_animation(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        angle: float = DEFAULT_WORRIED_ANGLE,
        height: float = 0.04,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.pose_animation(
            left_height=height,
            right_height=height,
            left_angle=abs(angle),
            right_angle=-abs(angle),
            duration=duration,
            rate_func=rate_func,
        )

    def worried(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        angle: float = DEFAULT_WORRIED_ANGLE,
        height: float = 0.04,
        rate_func=smooth,
    ) -> CharacterEyebrows:
        self.scene.play(
            self.worried_animation(
                duration,
                angle=angle,
                height=height,
                rate_func=rate_func,
            )
        )
        return self

    def cock_animation(
        self,
        side: BrowSide = "right",
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_RAISE,
        angle: float = 8 * np.pi / 180,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        if side == "left":
            return self.pose_animation(
                left_height=amount,
                left_angle=angle,
                duration=duration,
                rate_func=rate_func,
            )
        if side == "right":
            return self.pose_animation(
                right_height=amount,
                right_angle=-angle,
                duration=duration,
                rate_func=rate_func,
            )
        raise ValueError("side must be 'left' or 'right'")

    def cock(
        self,
        side: BrowSide = "right",
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_RAISE,
        angle: float = 8 * np.pi / 180,
        rate_func=smooth,
    ) -> CharacterEyebrows:
        self.scene.play(
            self.cock_animation(
                side,
                duration,
                amount=amount,
                angle=angle,
                rate_func=rate_func,
            )
        )
        return self


class CharacterMouthController:
    """High-level mouth controller exposed as ``actor.mouth``."""

    DEFAULT_DURATION = 0.3

    def __init__(self, scene: ThreeDScene, character: BlockCharacter) -> None:
        self.scene = scene
        self.character = character

    @property
    def mob(self) -> CharacterMouth:
        if not self.character.has_mouth:
            raise RuntimeError("This character has no mouth")
        return self.character.mouth

    def pose_animation(
        self,
        *,
        curve: float = 0.0,
        open_amount: float = 0.0,
        width: float | None = None,
        open_height: float | None = None,
        duration: float = DEFAULT_DURATION,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.mob.pose_animation(
            curve=curve,
            open_amount=open_amount,
            width=width,
            open_height=open_height,
            run_time=duration,
            rate_func=rate_func,
        )

    def pose(self, **kwargs) -> CharacterMouthController:
        self.scene.play(self.pose_animation(**kwargs))
        return self

    move_animation = pose_animation
    move = pose

    def neutral_animation(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.pose_animation(
            curve=0.0,
            open_amount=0.0,
            duration=duration,
            rate_func=rate_func,
        )

    def neutral(self, duration: float = DEFAULT_DURATION, *, rate_func=smooth) -> CharacterMouthController:
        self.scene.play(self.neutral_animation(duration, rate_func=rate_func))
        return self

    def smile_animation(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = 0.85,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.pose_animation(
            curve=abs(amount),
            open_amount=0.0,
            duration=duration,
            rate_func=rate_func,
        )

    def smile(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = 0.85,
        rate_func=smooth,
    ) -> CharacterMouthController:
        self.scene.play(
            self.smile_animation(duration, amount=amount, rate_func=rate_func)
        )
        return self

    def frown_animation(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = 0.75,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.pose_animation(
            curve=-abs(amount),
            open_amount=0.0,
            duration=duration,
            rate_func=rate_func,
        )

    def frown(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = 0.75,
        rate_func=smooth,
    ) -> CharacterMouthController:
        self.scene.play(
            self.frown_animation(duration, amount=amount, rate_func=rate_func)
        )
        return self

    def open_animation(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = 1.0,
        width: float = CharacterMouth.DEFAULT_WIDTH,
        height: float = CharacterMouth.DEFAULT_OPEN_HEIGHT,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.pose_animation(
            curve=0.0,
            open_amount=amount,
            width=width,
            open_height=height,
            duration=duration,
            rate_func=rate_func,
        )

    def open(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = 1.0,
        width: float = CharacterMouth.DEFAULT_WIDTH,
        height: float = CharacterMouth.DEFAULT_OPEN_HEIGHT,
        rate_func=smooth,
    ) -> CharacterMouthController:
        self.scene.play(
            self.open_animation(
                duration,
                amount=amount,
                width=width,
                height=height,
                rate_func=rate_func,
            )
        )
        return self

    close_animation = neutral_animation
    close = neutral

    def surprised_animation(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.open_animation(
            duration,
            amount=1.0,
            width=0.34,
            height=0.38,
            rate_func=rate_func,
        )

    def surprised(
        self,
        duration: float = DEFAULT_DURATION,
        *,
        rate_func=smooth,
    ) -> CharacterMouthController:
        self.scene.play(
            self.surprised_animation(duration, rate_func=rate_func)
        )
        return self
__all__ = ["BrowSide", "CharacterEyebrows", "CharacterMouthController"]
