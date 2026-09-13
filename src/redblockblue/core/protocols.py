"""Structural contracts for semantic scene objects."""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from manim import Animation, Mobject


@runtime_checkable
class SemanticObject(Protocol):
    """Anything with a primary Manim representation."""

    @property
    def mob(self) -> Mobject: ...


@runtime_checkable
class Presentable(Protocol):
    """A component that knows how to enter and leave a scene."""

    def show(self, *args, **kwargs) -> Animation: ...
    def hide(self, *args, **kwargs) -> Animation: ...


__all__ = ["SemanticObject", "Presentable"]
