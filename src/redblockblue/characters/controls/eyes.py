"""Semantic eye controls: gaze, tracking, pupil pose, lids, and blinking."""

from __future__ import annotations

from typing import Any

import numpy as np
from manim import (
    Animation,
    AnimationGroup,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Mobject,
    ORIGIN,
    ThreeDScene,
    UpdateFromAlphaFunc,
    VGroup,
    interpolate,
    linear,
    smooth,
)

from ...core.geometry import EPSILON
from ...core.targets import resolve_target_point, resolve_target_source
from ...core.timing import positive_time
from ..rig.character import BlockCharacter


EYE_DIRECTION_NAMES = {
    "centre": ORIGIN,
    "center": ORIGIN,
    "left": LEFT,
    "right": RIGHT,
    "up": UP,
    "down": DOWN,
    "up_left": UP + LEFT,
    "up_right": UP + RIGHT,
    "down_left": DOWN + LEFT,
    "down_right": DOWN + RIGHT,
}


def eye_offset_from_direction(direction: str | np.ndarray, amount: float) -> tuple[float, float]:
    if isinstance(direction, str):
        try:
            direction = EYE_DIRECTION_NAMES[direction.lower()]
        except KeyError as exc:
            valid = ", ".join(sorted(EYE_DIRECTION_NAMES))
            raise ValueError(
                f"Unknown eye direction {direction!r}. Choose from: {valid}"
            ) from exc
    planar = np.asarray(direction, dtype=float)[:2]
    length = np.linalg.norm(planar)
    if length < EPSILON:
        return 0.0, 0.0
    planar = float(amount) * planar / length
    return float(planar[0]), float(planar[1])


class CharacterEyes:
    """High-level eye controller exposed as ``actor.eyes``."""

    DEFAULT_DURATION = 0.4
    DEFAULT_AMOUNT = 0.06
    DEFAULT_BLINK_CLOSE_DURATION = 0.12
    DEFAULT_BLINK_OPEN_DURATION = 0.16
    DEFAULT_SQUINT_UPPER = 0.55
    DEFAULT_SQUINT_LOWER = 0.35
    DEFAULT_SUSPICIOUS_UPPER = 0.38
    DEFAULT_SUSPICIOUS_LOWER = 0.18

    def __init__(self, scene: ThreeDScene, character: BlockCharacter) -> None:
        self.scene = scene
        self.character = character
        self._tracking_updater = None

    @property
    def mob(self) -> VGroup:
        """Return the underlying eye geometry."""
        return self.character.eyes

    @property
    def is_tracking(self) -> bool:
        return self._tracking_updater is not None

    _target_source = staticmethod(resolve_target_source)
    _target_point = staticmethod(resolve_target_point)

    @staticmethod
    def _local_direction(
        eyes: VGroup,
        target_point: np.ndarray,
    ) -> np.ndarray:
        reference_eye = eyes[0]
        local_right, local_up, _normal = reference_eye.local_basis()
        displacement = target_point - reference_eye.get_center()

        return np.array(
            [
                np.dot(displacement, local_right),
                np.dot(displacement, local_up),
            ],
            dtype=float,
        )

    @classmethod
    def _set_look_at(
        cls,
        eyes: VGroup,
        target_point: np.ndarray,
        amount: float,
    ) -> None:
        reference_eye = eyes[0]
        local_right, local_up, normal = reference_eye.local_basis()
        displacement = target_point - reference_eye.get_center()
        direction = np.array(
            [
                np.dot(displacement, local_right),
                np.dot(displacement, local_up),
            ],
            dtype=float,
        )
        length = np.linalg.norm(direction)

        x, y = (
            (0.0, 0.0)
            if length < 1e-8
            else amount * direction / length
        )
        x = float(x)
        y = float(y)

        # Both eyes share the same rigid face basis. Reuse it instead of
        # recalculating local orientation for each pupil on every tracking frame.
        for eye in eyes:
            centre = np.asarray(eye.outer.get_center(), dtype=float)
            pupil_depth = float(
                np.dot(eye.pupil.get_center() - centre, normal)
            )
            eye.pupil.move_to(
                centre
                + x * local_right
                + y * local_up
                + pupil_depth * normal
            )

    # ----- Pupil tracking ------------------------------------------------

    def track(
        self,
        target: Any,
        *,
        amount: float = DEFAULT_AMOUNT,
    ) -> CharacterEyes:
        """Continuously point both pupils towards ``target``."""
        amount = float(amount)

        if amount < 0:
            raise ValueError("amount must be non-negative")

        self.stop_tracking()
        source = self._target_source(target)

        set_look_at = type(self)._set_look_at
        target_point = type(self)._target_point

        def update_tracking(
            eyes: VGroup,
        ) -> None:
            set_look_at(
                eyes,
                target_point(source),
                amount,
            )

        self._tracking_updater = update_tracking
        self.mob.add_updater(update_tracking)
        update_tracking(self.mob)
        return self

    def stop_tracking(self) -> CharacterEyes:
        """Stop continuous tracking and leave the pupils in place."""
        if self._tracking_updater is not None:
            self.mob.remove_updater(self._tracking_updater)
            self._tracking_updater = None

        return self

    # ----- Pupil movement ------------------------------------------------

    def look_animation(
        self,
        direction: str | np.ndarray = ORIGIN,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_AMOUNT,
    ) -> AnimationGroup:
        x, y = eye_offset_from_direction(direction, amount)

        return self.character.look(
            x=x,
            y=y,
            run_time=positive_time(duration),
        )

    def look(
        self,
        direction: str | np.ndarray = ORIGIN,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_AMOUNT,
    ) -> CharacterEyes:
        self.stop_tracking()
        self.scene.play(
            self.look_animation(
                direction,
                duration,
                amount=amount,
            )
        )
        return self

    move_pupils_animation = look_animation
    move_pupils = look

    def look_at_animation(
        self,
        target: Any,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_AMOUNT,
    ) -> AnimationGroup:
        source = self._target_source(target)
        direction = self._local_direction(
            self.mob,
            self._target_point(source),
        )

        return self.look_animation(
            direction,
            duration,
            amount=amount,
        )

    def look_at(
        self,
        target: Any,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_AMOUNT,
    ) -> CharacterEyes:
        self.stop_tracking()
        self.scene.play(
            self.look_at_animation(
                target,
                duration,
                amount=amount,
            )
        )
        return self

    def centre_animation(
        self,
        duration: float = DEFAULT_DURATION,
    ) -> AnimationGroup:
        """Return an animation that centres both pupils."""
        return self.look_animation(ORIGIN, duration)

    center_animation = centre_animation
    centre_pupils_animation = centre_animation
    center_pupils_animation = centre_animation

    def centre(
        self,
        duration: float = DEFAULT_DURATION,
    ) -> CharacterEyes:
        """Stop tracking and return both pupils to the centre."""
        self.stop_tracking()
        self.scene.play(self.centre_animation(duration))
        return self

    center = centre
    centre_pupils = centre
    center_pupils = centre

    def pupil_pose_animation(
        self,
        direction: str | np.ndarray = ORIGIN,
        scale: float = 1.0,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_AMOUNT,
        rate_func=smooth,
    ) -> AnimationGroup:
        """Animate pupil position and size together without overlapping animations."""
        duration = positive_time(duration)
        x, y = eye_offset_from_direction(direction, amount)
        animations = []

        for eye in self.mob:
            start_center = np.asarray(eye.pupil.get_center(), dtype=float).copy()
            end_center = np.asarray(eye.pupil_target(x=x, y=y), dtype=float)
            start_scale = float(eye.pupil_scale)
            end_scale = eye._clamp_pupil_scale(scale)

            def update_pupil(
                pupil: Mobject,
                alpha: float,
                *,
                eye=eye,
                start_center=start_center,
                end_center=end_center,
                start_scale=start_scale,
                end_scale=end_scale,
            ) -> None:
                target_scale = float(interpolate(start_scale, end_scale, alpha))
                factor = target_scale / eye._pupil_scale
                if abs(factor - 1.0) > 1e-12:
                    pupil.scale(factor, about_point=pupil.get_center())
                eye._pupil_scale = target_scale
                pupil.move_to(interpolate(start_center, end_center, alpha))

            animations.append(
                UpdateFromAlphaFunc(
                    eye.pupil,
                    update_pupil,
                    run_time=duration,
                    rate_func=rate_func,
                )
            )

        return AnimationGroup(
            *animations,
            lag_ratio=0,
            run_time=duration,
        )

    # ----- Pupil size ----------------------------------------------------

    def pupil_scale_animation(
        self,
        scale: float = 1.0,
        duration: float = 0.3,
        *,
        rate_func=smooth,
    ) -> AnimationGroup:
        """Animate both pupils to the same size multiplier."""
        duration = positive_time(duration)
        return AnimationGroup(
            *(
                eye.pupil_scale_animation(
                    scale,
                    run_time=duration,
                    rate_func=rate_func,
                )
                for eye in self.mob
            ),
            lag_ratio=0,
            run_time=duration,
        )

    resize_pupils_animation = pupil_scale_animation

    def pupil_scale(
        self,
        scale: float = 1.0,
        duration: float = 0.3,
        *,
        rate_func=smooth,
    ) -> CharacterEyes:
        """Set both pupil sizes with an animation."""
        self.scene.play(
            self.pupil_scale_animation(
                scale,
                duration,
                rate_func=rate_func,
            )
        )
        return self

    resize_pupils = pupil_scale

    # ----- Eyelid movement ----------------------------------------------

    def lids_animation(
        self,
        *,
        upper: float = 0.0,
        lower: float = 0.0,
        duration: float = 0.3,
        rate_func=smooth,
    ) -> AnimationGroup:
        """Move the upper and lower eyelids independently.

        ``0`` means fully out of sight. ``1`` means that lid reaches the
        centre of the eye.
        """
        return self.character.lids_animation(
            upper=upper,
            lower=lower,
            run_time=positive_time(duration),
            rate_func=rate_func,
        )

    def lids(
        self,
        *,
        upper: float = 0.0,
        lower: float = 0.0,
        duration: float = 0.3,
        rate_func=smooth,
    ) -> CharacterEyes:
        self.scene.play(
            self.lids_animation(
                upper=upper,
                lower=lower,
                duration=duration,
                rate_func=rate_func,
            )
        )
        return self

    move_eyelids_animation = lids_animation
    move_eyelids = lids

    def squint_animation(
        self,
        duration: float = 0.3,
        *,
        upper: float = DEFAULT_SQUINT_UPPER,
        lower: float = DEFAULT_SQUINT_LOWER,
        rate_func=smooth,
    ) -> AnimationGroup:
        """Return an animation that narrows both eyes."""
        return self.lids_animation(
            upper=upper,
            lower=lower,
            duration=duration,
            rate_func=rate_func,
        )

    def squint(
        self,
        duration: float = 0.3,
        *,
        upper: float = DEFAULT_SQUINT_UPPER,
        lower: float = DEFAULT_SQUINT_LOWER,
        rate_func=smooth,
    ) -> CharacterEyes:
        self.scene.play(
            self.squint_animation(
                duration,
                upper=upper,
                lower=lower,
                rate_func=rate_func,
            )
        )
        return self

    def suspicious_animation(
        self,
        direction: str | np.ndarray = LEFT,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_AMOUNT,
        upper: float = DEFAULT_SUSPICIOUS_UPPER,
        lower: float = DEFAULT_SUSPICIOUS_LOWER,
        rate_func=smooth,
    ) -> AnimationGroup:
        """Look sideways while narrowing both eyes."""
        duration = positive_time(duration)
        return AnimationGroup(
            self.look_animation(
                direction,
                duration,
                amount=amount,
            ),
            self.lids_animation(
                upper=upper,
                lower=lower,
                duration=duration,
                rate_func=rate_func,
            ),
            lag_ratio=0,
            run_time=duration,
        )

    def suspicious(
        self,
        direction: str | np.ndarray = LEFT,
        duration: float = DEFAULT_DURATION,
        *,
        amount: float = DEFAULT_AMOUNT,
        upper: float = DEFAULT_SUSPICIOUS_UPPER,
        lower: float = DEFAULT_SUSPICIOUS_LOWER,
        rate_func=smooth,
    ) -> CharacterEyes:
        self.stop_tracking()
        self.scene.play(
            self.suspicious_animation(
                direction,
                duration,
                amount=amount,
                upper=upper,
                lower=lower,
                rate_func=rate_func,
            )
        )
        return self

    # ----- Open, close, and blink ---------------------------------------

    def open_animation(
        self,
        duration: float = 0.3,
        *,
        rate_func=smooth,
    ) -> AnimationGroup:
        return self.lids_animation(
            upper=0.0,
            lower=0.0,
            duration=duration,
            rate_func=rate_func,
        )

    def close_animation(
        self,
        duration: float = 0.3,
        *,
        rate_func=smooth,
    ) -> AnimationGroup:
        return self.lids_animation(
            upper=1.0,
            lower=1.0,
            duration=duration,
            rate_func=rate_func,
        )

    def open(
        self,
        duration: float = 0.3,
        *,
        rate_func=smooth,
    ) -> CharacterEyes:
        self.scene.play(
            self.open_animation(
                duration,
                rate_func=rate_func,
            )
        )
        return self

    def close(
        self,
        duration: float = 0.3,
        *,
        rate_func=smooth,
    ) -> CharacterEyes:
        self.scene.play(
            self.close_animation(
                duration,
                rate_func=rate_func,
            )
        )
        return self

    def blink_animation(
        self,
        *,
        close_duration: float = DEFAULT_BLINK_CLOSE_DURATION,
        open_duration: float = DEFAULT_BLINK_OPEN_DURATION,
    ) -> Animation:
        """Close and reopen, restoring the current eyelid expression."""
        close_duration = positive_time(close_duration)
        open_duration = positive_time(open_duration)
        total_duration = close_duration + open_duration
        close_fraction = close_duration / total_duration

        start_lids = [
            (
                float(eye.upper_lid_amount),
                float(eye.lower_lid_amount),
            )
            for eye in self.mob
        ]

        def update_blink(eyes: VGroup, alpha: float) -> None:
            if alpha <= close_fraction:
                phase = smooth(alpha / close_fraction)
            else:
                reopen_alpha = (
                    alpha - close_fraction
                ) / (1.0 - close_fraction)
                phase = smooth(1.0 - reopen_alpha)

            for eye, (start_upper, start_lower) in zip(
                eyes,
                start_lids,
            ):
                eye._upper_lid_amount = interpolate(
                    start_upper,
                    1.0,
                    phase,
                )
                eye._lower_lid_amount = interpolate(
                    start_lower,
                    1.0,
                    phase,
                )
                eye._apply_eye_state()

        return UpdateFromAlphaFunc(
            self.mob,
            update_blink,
            run_time=total_duration,
            rate_func=linear,
        )

    def blink(
        self,
        *,
        close_duration: float = DEFAULT_BLINK_CLOSE_DURATION,
        open_duration: float = DEFAULT_BLINK_OPEN_DURATION,
    ) -> CharacterEyes:
        self.scene.play(
            self.blink_animation(
                close_duration=close_duration,
                open_duration=open_duration,
            )
        )
        return self


__all__ = ["CharacterEyes", "EYE_DIRECTION_NAMES", "eye_offset_from_direction"]
