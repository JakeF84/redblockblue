"""Typed, inspectable presentation style registries."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CodeStyle(str, Enum):
    CLEAN = "clean"
    LIVE_CODING = "live_coding"
    WALKTHROUGH = "walkthrough"
    ENERGETIC = "energetic"
    DRAMATIC = "dramatic"
    TECHNICAL = "technical"


@dataclass(frozen=True, slots=True)
class CodeStyleSpec:
    formatter_style: str
    run_time: float
    entrance: str


CODE_STYLES: dict[str, CodeStyleSpec] = {
    "clean": CodeStyleSpec("monokai", 1.0, "clean"),
    "live_coding": CodeStyleSpec("monokai", 2.4, "typing"),
    "walkthrough": CodeStyleSpec("monokai", 1.8, "line_by_line"),
    "energetic": CodeStyleSpec("monokai", 0.75, "slide"),
    "dramatic": CodeStyleSpec("monokai", 1.8, "dramatic"),
    "technical": CodeStyleSpec("native", 1.25, "technical"),
}


class QuoteStyle(str, Enum):
    MINIMAL = "minimal"
    PORTRAIT_LEFT = "portrait_left"
    PORTRAIT_RIGHT = "portrait_right"
    CINEMATIC = "cinematic"
    EDITORIAL = "editorial"
    CARD = "card"
    TYPEWRITER = "typewriter"
    LINE_BY_LINE = "line_by_line"
    LETTER_BY_LETTER = "letter_by_letter"
    SPOTLIGHT = "spotlight"
    KINETIC = "kinetic"
    ARCHIVAL = "archival"
    SPLIT = "split"
    FRAMED = "framed"
    PULL_QUOTE = "pull_quote"
    CENTERED_PORTRAIT = "centered_portrait"
    LOWER_THIRD = "lower_third"
    QUOTE_MARKS = "quote_marks"
    FLOATING_CARD = "floating_card"
    MONOCHROME = "monochrome"


@dataclass(frozen=True, slots=True)
class QuoteStyleSpec:
    layout: str
    entrance: str
    background: str
    image_treatment: str
    quote_font_size: int
    author_font_size: int


QUOTE_STYLES: dict[str, QuoteStyleSpec] = {
    "minimal": QuoteStyleSpec("center", "fade", "none", "plain", 42, 26),
    "portrait_left": QuoteStyleSpec("portrait_left", "image_then_text", "none", "circle", 38, 24),
    "portrait_right": QuoteStyleSpec("portrait_right", "text_then_image", "none", "circle", 38, 24),
    "cinematic": QuoteStyleSpec("cinematic", "cinematic", "dim", "hero", 44, 25),
    "editorial": QuoteStyleSpec("editorial", "line_reveal", "none", "square", 42, 22),
    "card": QuoteStyleSpec("card", "card", "card", "circle", 38, 23),
    "typewriter": QuoteStyleSpec("center", "letters", "none", "plain", 40, 24),
    "line_by_line": QuoteStyleSpec("center", "line_reveal", "none", "plain", 42, 24),
    "letter_by_letter": QuoteStyleSpec("center", "letters_slow", "none", "plain", 40, 24),
    "spotlight": QuoteStyleSpec("center", "spotlight", "spotlight", "circle", 42, 24),
    "kinetic": QuoteStyleSpec("center", "kinetic", "none", "plain", 46, 24),
    "archival": QuoteStyleSpec("archival", "archival", "archive", "square", 36, 22),
    "split": QuoteStyleSpec("split", "split", "none", "square", 40, 24),
    "framed": QuoteStyleSpec("center", "frame", "frame", "plain", 40, 24),
    "pull_quote": QuoteStyleSpec("pull_quote", "pull_quote", "none", "plain", 50, 24),
    "centered_portrait": QuoteStyleSpec("centered_portrait", "portrait_pop", "none", "circle", 36, 23),
    "lower_third": QuoteStyleSpec("lower_third", "lower_third", "lower_third", "circle", 30, 21),
    "quote_marks": QuoteStyleSpec("quote_marks", "quote_marks", "none", "plain", 42, 23),
    "floating_card": QuoteStyleSpec("card", "floating_card", "card", "circle", 38, 23),
    "monochrome": QuoteStyleSpec("monochrome", "monochrome", "none", "square", 38, 22),
}


def style_name(style: str | Enum) -> str:
    return style.value if isinstance(style, Enum) else str(style)


__all__ = [
    "CodeStyle", "CodeStyleSpec", "CODE_STYLES",
    "QuoteStyle", "QuoteStyleSpec", "QUOTE_STYLES", "style_name",
]
