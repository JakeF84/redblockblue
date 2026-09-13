"""Compatibility routes for the prototype API.

New code should prefer semantic actor verbs plus namespaced primitive controls.
This bridge keeps old scenes running without letting CharacterActor grow into a
thousand-line forwarding class again.
"""

from __future__ import annotations

import warnings

_CONTROLLER_ROUTES = {
    # eyes
    "move_pupils_animation": ("eyes", "move_pupils_animation"),
    "eye_animation": ("eyes", "move_pupils_animation"),
    "move_pupils": ("eyes", "move_pupils"),
    "move_eyes": ("eyes", "move_pupils"),
    "centre_pupils_animation": ("eyes", "centre_animation"),
    "center_pupils_animation": ("eyes", "centre_animation"),
    "centre_pupils": ("eyes", "centre"),
    "center_pupils": ("eyes", "centre"),
    "pupil_scale_animation": ("eyes", "pupil_scale_animation"),
    "resize_pupils_animation": ("eyes", "pupil_scale_animation"),
    "pupil_scale": ("eyes", "pupil_scale"),
    "resize_pupils": ("eyes", "pupil_scale"),
    "move_eyelids_animation": ("eyes", "move_eyelids_animation"),
    "move_eyelids": ("eyes", "move_eyelids"),
    "squint_animation": ("eyes", "squint_animation"),
    "squint": ("eyes", "squint"),
    "suspicious_animation": ("eyes", "suspicious_animation"),
    "suspicious": ("eyes", "suspicious"),
    "open_eyes_animation": ("eyes", "open_animation"),
    "close_eyes_animation": ("eyes", "close_animation"),
    "open_eyes": ("eyes", "open"),
    "close_eyes": ("eyes", "close"),
    "blink_animation": ("eyes", "blink_animation"),
    "blink": ("eyes", "blink"),
    # eyebrows
    "move_eyebrows_animation": ("eyebrows", "move_animation"),
    "move_eyebrows": ("eyebrows", "move"),
    "neutral_eyebrows_animation": ("eyebrows", "neutral_animation"),
    "neutral_eyebrows": ("eyebrows", "neutral"),
    "raise_eyebrows_animation": ("eyebrows", "raise_animation"),
    "raise_eyebrows": ("eyebrows", "raise_"),
    "lower_eyebrows_animation": ("eyebrows", "lower_animation"),
    "lower_eyebrows": ("eyebrows", "lower"),
    "furrow_eyebrows_animation": ("eyebrows", "furrow_animation"),
    "furrow_eyebrows": ("eyebrows", "furrow"),
    "worried_eyebrows_animation": ("eyebrows", "worried_animation"),
    "worried_eyebrows": ("eyebrows", "worried"),
    "cock_eyebrow_animation": ("eyebrows", "cock_animation"),
    "cock_eyebrow": ("eyebrows", "cock"),
    # mouth
    "move_mouth_animation": ("mouth", "move_animation"),
    "move_mouth": ("mouth", "move"),
    "neutral_mouth_animation": ("mouth", "neutral_animation"),
    "neutral_mouth": ("mouth", "neutral"),
    "smile_animation": ("mouth", "smile_animation"),
    "smile": ("mouth", "smile"),
    "frown_animation": ("mouth", "frown_animation"),
    "frown": ("mouth", "frown"),
    "open_mouth_animation": ("mouth", "open_animation"),
    "open_mouth": ("mouth", "open"),
    "close_mouth_animation": ("mouth", "close_animation"),
    "close_mouth": ("mouth", "close"),
    "surprised_mouth_animation": ("mouth", "surprised_animation"),
    "surprised_mouth": ("mouth", "surprised"),
}

_EXPRESSION_SHORTCUTS = {
    "neutral_expression": "neutral",
    "happy": "happy",
    "sad": "sad",
    "angry": "angry",
    "surprised": "surprised",
}


class LegacyActorAPI:
    def __getattr__(self, name: str):
        route = _CONTROLLER_ROUTES.get(name)
        if route is not None:
            controller_name, method_name = route
            method = getattr(getattr(self, controller_name), method_name)
            if name.endswith("_animation") or name == "eye_animation":
                return method

            def action(*args, **kwargs):
                warnings.warn(
                    f"CharacterActor.{name}() is a compatibility shortcut; "
                    f"prefer actor.{controller_name}.{method_name}().",
                    DeprecationWarning,
                    stacklevel=2,
                )
                method(*args, **kwargs)
                return self
            return action

        base = name[:-10] if name.endswith("_animation") else name
        preset = _EXPRESSION_SHORTCUTS.get(base)
        if preset is not None:
            if name.endswith("_animation"):
                return lambda *args, **kwargs: self.expressions.animation(preset, *args, **kwargs)

            def expression(*args, **kwargs):
                self.expressions.apply(preset, *args, **kwargs)
                return self
            return expression

        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

    def __dir__(self):
        legacy = set(_CONTROLLER_ROUTES)
        legacy.update(_EXPRESSION_SHORTCUTS)
        legacy.update(f"{name}_animation" for name in _EXPRESSION_SHORTCUTS)
        return sorted(set(super().__dir__()) | legacy)


__all__ = ["LegacyActorAPI"]
