"""RedBlockBlue semantic animation layer for Manim.

The new package deliberately does not wildcard-re-export Manim. Import Manim
normally, then import the semantic vocabulary you need from here.
"""

from .characters import CharacterActor, EXPRESSION_PRESETS, ExpressionPose
from .presentation import CodeStyle, CodeWindow, Quote, QuoteStyle
from .scene import CharacterScene, RBBScene

__version__ = "0.1.0"

__all__ = [
    "RBBScene", "CharacterScene", "CharacterActor", "ExpressionPose",
    "EXPRESSION_PRESETS", "CodeWindow", "CodeStyle", "Quote", "QuoteStyle",
]
