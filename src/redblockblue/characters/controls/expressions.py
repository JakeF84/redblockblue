"""Compose primitive controls into named, data-driven expressions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from manim import Animation, AnimationGroup, smooth

from ...core.timing import positive_time
from ..presets import EXPRESSION_PRESETS, ExpressionPose

if TYPE_CHECKING:
    from ..actor import CharacterActor

class CharacterExpressions:
    """Data-driven expression controller exposed as ``actor.expressions``.

    Every preset can be called directly, for example::

        red.expressions.sad()
        red.expressions.shocked(duration=0.2)
        self.play(red.expressions.sceptical_animation())

    ``apply(name)`` and ``animation(name)`` are also available for dynamic use.
    """

    DEFAULT_DURATION = 0.4

    def __init__(self, actor: CharacterActor) -> None:
        self.actor = actor
        self.scene = actor.scene
        self.character = actor.character

    @property
    def presets(self) -> dict[str, ExpressionPose]:
        """Return a copy of the preset mapping for safe inspection."""
        return dict(EXPRESSION_PRESETS)

    def available(self) -> tuple[str, ...]:
        """Return all expression names in stable definition order."""
        return tuple(EXPRESSION_PRESETS)

    def pose(self, name: str) -> ExpressionPose:
        """Return the immutable pose data for ``name``."""
        try:
            return EXPRESSION_PRESETS[name]
        except KeyError as exc:
            valid = ", ".join(EXPRESSION_PRESETS)
            raise ValueError(
                f"Unknown expression {name!r}. Choose from: {valid}"
            ) from exc

    def animation(
        self,
        name: str,
        duration: float = DEFAULT_DURATION,
        *,
        rate_func=smooth,
    ) -> AnimationGroup:
        """Build, but do not play, a complete facial expression animation."""
        duration = positive_time(duration)
        pose = self.pose(name)

        animations: list[Animation] = [
            self.actor.eyes.pupil_pose_animation(
                pose.gaze,
                pose.pupil_scale,
                duration,
                amount=pose.gaze_amount,
                rate_func=rate_func,
            ),
            self.actor.eyes.lids_animation(
                upper=pose.upper_lid,
                lower=pose.lower_lid,
                duration=duration,
                rate_func=rate_func,
            ),
        ]

        if self.character.has_eyebrows:
            animations.append(
                self.actor.eyebrows.pose_animation(
                    left_height=pose.left_brow_height,
                    right_height=pose.right_brow_height,
                    left_angle=pose.left_brow_angle,
                    right_angle=pose.right_brow_angle,
                    duration=duration,
                    rate_func=rate_func,
                )
            )

        if self.character.has_mouth:
            animations.append(
                self.actor.mouth.move_animation(
                    curve=pose.mouth_curve,
                    open_amount=pose.mouth_open,
                    width=pose.mouth_width,
                    open_height=pose.mouth_height,
                    duration=duration,
                    rate_func=rate_func,
                )
            )

        return AnimationGroup(
            *animations,
            lag_ratio=0,
            run_time=duration,
        )

    def apply(
        self,
        name: str,
        duration: float = DEFAULT_DURATION,
        *,
        rate_func=smooth,
    ) -> CharacterExpressions:
        """Play a named expression and stop any active gaze tracking first."""
        self.actor.stop_tracking()
        self.scene.play(
            self.animation(name, duration, rate_func=rate_func)
        )
        return self

    def __getattr__(self, name: str) -> Callable:
        """Expose every preset as ``name()`` and ``name_animation()``."""
        animation_suffix = "_animation"

        if name.endswith(animation_suffix):
            preset_name = name[:-len(animation_suffix)]
            if preset_name in EXPRESSION_PRESETS:
                def preset_animation(
                    duration: float = self.DEFAULT_DURATION,
                    *,
                    rate_func=smooth,
                ) -> AnimationGroup:
                    return self.animation(
                        preset_name,
                        duration,
                        rate_func=rate_func,
                    )
                return preset_animation

        if name in EXPRESSION_PRESETS:
            def preset_apply(
                duration: float = self.DEFAULT_DURATION,
                *,
                rate_func=smooth,
            ) -> CharacterExpressions:
                return self.apply(
                    name,
                    duration,
                    rate_func=rate_func,
                )
            return preset_apply

        raise AttributeError(
            f"{type(self).__name__!s} has no attribute {name!r}"
        )

    def __dir__(self) -> list[str]:
        dynamic = list(EXPRESSION_PRESETS)
        dynamic.extend(f"{name}_animation" for name in EXPRESSION_PRESETS)
        return sorted(set(super().__dir__()) | set(dynamic))
__all__ = ["CharacterExpressions"]
