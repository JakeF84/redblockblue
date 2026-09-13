from __future__ import annotations

from pathlib import Path
import textwrap

from manim import (
    Animation,
    AnimationGroup,
    BLACK,
    Circle,
    Create,
    DOWN,
    FadeIn,
    FadeOut,
    GRAY_A,
    GRAY_B,
    GRAY_C,
    GRAY_D,
    GRAY_E,
    Group,
    GrowFromCenter,
    ImageMobject,
    LEFT,
    LaggedStart,
    Line,
    Mobject,
    ORIGIN,
    RIGHT,
    Rectangle,
    RoundedRectangle,
    SurroundingRectangle,
    Text,
    UP,
    VGroup,
    Wait,
    Write,
    YELLOW,
    config,
)

from ..core.timing import positive_time
from .styles import QUOTE_STYLES, QuoteStyle, style_name

ImageInput = str | Path | Mobject | None


class Quote(Group):
    """Reusable quote component with a deliberately tiny public API.

    Quote(quote, author, image, style)

    `image` may be None, a path, or any Manim Mobject.
    """

    STYLES = QUOTE_STYLES

    def __init__(self, quote: str, author: str | None = None,
                 image: ImageInput = None, style: str | QuoteStyle = QuoteStyle.MINIMAL):
        super().__init__()
        if not quote.strip():
            raise ValueError("quote must contain non-whitespace text")
        style = style_name(style)
        if style not in self.STYLES:
            raise ValueError(f"Unknown style {style!r}. Choose from: {', '.join(self.STYLES)}")

        self.quote = quote
        self.author = author
        self.image_input = image
        self.style = style
        self.style_config = self.STYLES[style]
        self.layout = self.style_config.layout
        self.entrance = self.style_config.entrance
        self.bg_kind = self.style_config.background
        self.image_treatment = self.style_config.image_treatment
        qsize = self.style_config.quote_font_size
        asize = self.style_config.author_font_size

        self.decorations = VGroup()
        self.image_mob = self._make_image(image)
        self.quote_lines = self._make_quote(quote, qsize, self._max_quote_width(self.layout))
        self.author_mob = Text(f"— {author}", font_size=asize, color=GRAY_B) if author else None
        self.background = self._make_background(self.bg_kind)

        self._style_image()
        self._layout()

        visuals = (self.image_mob, self.background) if self.layout == "cinematic" else (self.background, self.image_mob)
        self.parts = [m for m in (*visuals, self.quote_lines,
                                  self.author_mob, self.decorations) if m is not None]
        self.add(*self.parts)

    @classmethod
    def available_styles(cls):
        return tuple(cls.STYLES)

    def show(self, run_time: float = 1.0) -> Animation:
        run_time = positive_time(run_time)
        return AnimationGroup(
            self._entrance_animation(run_time), group=self, run_time=run_time,
        )

    def hide(self, run_time: float = 0.5) -> Animation:
        return FadeOut(self, shift=DOWN * 0.06, run_time=positive_time(run_time))

    # ---------- building ----------

    def _max_quote_width(self, layout):
        return {
            "portrait_left": 6.8, "portrait_right": 6.8, "cinematic": 9.6,
            "editorial": 7.7, "card": 7.0, "archival": 6.8,
            "split": 6.0, "pull_quote": 9.0, "centered_portrait": 8.4,
            "lower_third": 8.0, "quote_marks": 8.2, "monochrome": 6.8,
        }.get(layout, 8.8)

    def _make_quote(self, text, font_size, max_width):
        lines = textwrap.wrap(text.strip(), width=max(20, int(max_width * 8.5)),
                              break_long_words=False) or [""]
        group = VGroup(*[Text(line, font_size=font_size) for line in lines])
        group.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        if group.width > max_width:
            group.scale_to_fit_width(max_width)
        return group

    def _make_image(self, image):
        if image is None:
            return None
        if isinstance(image, Mobject):
            return image.copy()
        path = Path(image)
        if not path.exists():
            raise FileNotFoundError(f"Quote image not found: {path}")
        return ImageMobject(str(path))

    def _make_background(self, kind):
        if kind == "none":
            return None
        if kind == "dim":
            return Rectangle(width=config.frame_width, height=config.frame_height,
                             stroke_width=0, fill_color=BLACK, fill_opacity=0.64)
        if kind == "spotlight":
            return RoundedRectangle(width=10.6, height=4.8, corner_radius=0.22,
                                    stroke_color=GRAY_D, stroke_width=1.5,
                                    fill_color=BLACK, fill_opacity=0.78)
        if kind == "card":
            return RoundedRectangle(width=10.5, height=4.8, corner_radius=0.24,
                                    stroke_color=GRAY_D, stroke_width=1.5,
                                    fill_color=BLACK, fill_opacity=0.88)
        if kind == "archive":
            return RoundedRectangle(width=10.8, height=5.1, corner_radius=0.08,
                                    stroke_color=GRAY_C, stroke_width=1.4,
                                    fill_color=GRAY_E, fill_opacity=0.96)
        if kind == "frame":
            return RoundedRectangle(width=10.8, height=5.3, corner_radius=0.15,
                                    stroke_color=GRAY_B, stroke_width=2, fill_opacity=0)
        if kind == "lower_third":
            return RoundedRectangle(width=11.7, height=2.2, corner_radius=0.16,
                                    stroke_width=0, fill_color=BLACK, fill_opacity=0.86)

    def _style_image(self):
        i = self.image_mob
        if i is None:
            return
        if self.image_treatment == "hero":
            i.scale_to_fit_height(config.frame_height * 0.92)
            if i.width < config.frame_width:
                i.scale_to_fit_width(config.frame_width * 0.92)
            return
        if self.image_treatment == "circle":
            i.scale_to_fit_height(2.0)
            self._image_frame = Circle(radius=1.05, stroke_color=GRAY_B, stroke_width=2)
            self.decorations.add(self._image_frame)
        elif self.image_treatment == "square":
            i.scale_to_fit_height(2.25)
            self._image_frame = SurroundingRectangle(i, buff=0.07, color=GRAY_B, stroke_width=1.5)
            self.decorations.add(self._image_frame)
        else:
            i.scale_to_fit_height(1.9)

    def _text_block(self, aligned_edge=LEFT, buff=0.32):
        mobs = [self.quote_lines] + ([self.author_mob] if self.author_mob else [])
        block = VGroup(*mobs).arrange(DOWN, aligned_edge=aligned_edge, buff=buff)
        return block

    def _sync_frame(self):
        if self.image_mob is not None and hasattr(self, "_image_frame"):
            self._image_frame.move_to(self.image_mob)

    # ---------- layouts ----------

    def _layout(self):
        q, a, i, b = self.quote_lines, self.author_mob, self.image_mob, self.background
        layout = self.layout

        if layout == "center":
            block = self._text_block()
            block.move_to(ORIGIN)
            if i is not None:
                i.next_to(block, UP, buff=0.4)
                self._sync_frame()

        elif layout in ("portrait_left", "portrait_right"):
            if i is None:
                self.layout = "center"; self._layout(); self.layout = layout; return
            block = self._text_block()
            pair = Group(i, block) if layout == "portrait_left" else Group(block, i)
            pair.arrange(RIGHT, buff=0.7).move_to(ORIGIN)
            self._sync_frame()

        elif layout == "cinematic":
            if i is not None:
                i.move_to(ORIGIN).set_opacity(0.45).set_z_index(-3)
            if b is not None:
                b.set_z_index(-2)
            q.move_to(DOWN * 0.15).set_z_index(2)
            if a:
                a.next_to(q, DOWN, aligned_edge=LEFT, buff=0.35).set_z_index(2)

        elif layout == "editorial":
            q.to_edge(LEFT, buff=1.3).shift(UP * 0.15)
            if a: a.next_to(q, DOWN, aligned_edge=LEFT, buff=0.35)
            bar = Rectangle(width=0.06, height=max(1.7, q.height + 0.8), stroke_width=0,
                            fill_color=YELLOW, fill_opacity=1).next_to(q, LEFT, buff=0.3)
            self.decorations.add(bar)
            if i is not None:
                i.to_edge(RIGHT, buff=1.0); self._sync_frame()

        elif layout == "card":
            if i is not None:
                i.move_to(LEFT * 3.5); self._sync_frame(); q.move_to(RIGHT * 1.15 + UP * 0.2)
            else:
                q.move_to(UP * 0.2)
            if a: a.next_to(q, DOWN, aligned_edge=LEFT, buff=0.32)

        elif layout == "archival":
            q.set_color(GRAY_A).move_to(RIGHT * 1.2 + UP * 0.15)
            if a: a.set_color(GRAY_B).next_to(q, DOWN, aligned_edge=LEFT, buff=0.35)
            if i is not None:
                i.move_to(LEFT * 3.65); self._sync_frame()
            self.decorations.add(Text("ARCHIVE", font_size=18, color=GRAY_C).move_to(UP * 2.1 + LEFT * 4.2))

        elif layout == "split":
            self.decorations.add(Line(UP * 2.2, DOWN * 2.2, color=GRAY_D, stroke_width=1.5))
            if i is not None:
                i.move_to(LEFT * 3.35); self._sync_frame()
            q.move_to(RIGHT * 3.0 + UP * 0.15)
            if a: a.next_to(q, DOWN, aligned_edge=LEFT, buff=0.35)

        elif layout == "pull_quote":
            q.move_to(ORIGIN)
            if a: a.next_to(q, DOWN, buff=0.45)
            top = Line(LEFT * 4.7, RIGHT * 4.7, color=GRAY_D, stroke_width=1.5).next_to(q, UP, buff=0.6)
            bottom_anchor = a if a else q
            bottom = Line(LEFT * 4.7, RIGHT * 4.7, color=GRAY_D, stroke_width=1.5).next_to(bottom_anchor, DOWN, buff=0.55)
            self.decorations.add(top, bottom)

        elif layout == "centered_portrait":
            if i is not None:
                i.move_to(UP * 1.55); self._sync_frame()
            q.move_to(DOWN * 0.45)
            if a: a.next_to(q, DOWN, buff=0.28)

        elif layout == "lower_third":
            anchor = DOWN * 2.15
            if b is not None: b.to_edge(DOWN, buff=0.22)
            if i is not None:
                i.scale_to_fit_height(1.35).move_to(LEFT * 4.8 + anchor)
                if hasattr(self, "_image_frame"):
                    self._image_frame.scale(0.67); self._sync_frame()
            q.move_to(LEFT * 0.3 + anchor + UP * 0.18)
            if q.width > 8.2: q.scale_to_fit_width(8.2)
            if a: a.next_to(q, DOWN, aligned_edge=LEFT, buff=0.15)

        elif layout == "quote_marks":
            q.move_to(ORIGIN)
            if a: a.next_to(q, DOWN, buff=0.38)
            lq = Text("“", font_size=120, color=GRAY_D).next_to(q, LEFT, buff=0.3).shift(UP * 0.6)
            rq = Text("”", font_size=120, color=GRAY_D).next_to(q, RIGHT, buff=0.3).shift(DOWN * 0.15)
            self.decorations.add(lq, rq)

        elif layout == "monochrome":
            q.set_color(GRAY_A).move_to(RIGHT * 1.4)
            if a: a.set_color(GRAY_C).next_to(q, DOWN, aligned_edge=LEFT, buff=0.32)
            if i is not None:
                i.set_opacity(0.72).move_to(LEFT * 3.7); self._sync_frame()

    # ---------- entrance animations ----------

    def _entrance_animation(self, run_time):
        q, a, i, b, d = self.quote_lines, self.author_mob, self.image_mob, self.background, self.decorations
        name = self.entrance

        def seq(*anims):
            return AnimationGroup(*[x for x in anims if x is not None], lag_ratio=1, run_time=run_time)

        if name == "fade":
            return AnimationGroup(*[FadeIn(m, shift=UP * 0.06) for m in self.parts], lag_ratio=0.06, run_time=run_time)
        if name == "image_then_text":
            return seq(FadeIn(i, scale=0.88) if i is not None else None, FadeIn(d) if len(d) else None,
                       FadeIn(q, shift=RIGHT * 0.18), FadeIn(a) if a else None)
        if name == "text_then_image":
            return seq(FadeIn(q, shift=LEFT * 0.18), FadeIn(a) if a else None,
                       FadeIn(i, scale=0.88) if i is not None else None, FadeIn(d) if len(d) else None)
        if name == "cinematic":
            lines = LaggedStart(*[FadeIn(line, shift=UP * 0.12) for line in q], lag_ratio=0.18)
            return seq(FadeIn(i, scale=1.04) if i is not None else None, FadeIn(b) if b else None, lines, FadeIn(a) if a else None)
        if name == "line_reveal":
            lines = LaggedStart(*[FadeIn(line, shift=RIGHT * 0.18) for line in q], lag_ratio=0.16)
            return seq(FadeIn(b) if b else None, FadeIn(i, scale=0.92) if i is not None else None,
                       FadeIn(d) if len(d) else None, lines, FadeIn(a) if a else None)
        if name == "card":
            return seq(GrowFromCenter(b) if b else None, FadeIn(i, scale=0.85) if i is not None else None,
                       FadeIn(d) if len(d) else None, FadeIn(q, shift=UP * 0.12), FadeIn(a) if a else None)
        if name in ("letters", "letters_slow"):
            glyphs = [FadeIn(g, shift=RIGHT * 0.02) for line in q for g in line]
            main = LaggedStart(*glyphs, lag_ratio=0.015 if name == "letters" else 0.035)
            return seq(FadeIn(i) if i is not None else None, main, FadeIn(a, shift=UP * 0.05) if a else None)
        if name == "spotlight":
            return seq(FadeIn(b, scale=0.96) if b else None, FadeIn(i, scale=0.88) if i is not None else None,
                       FadeIn(d) if len(d) else None, Write(q), FadeIn(a) if a else None)
        if name == "kinetic":
            dirs = [LEFT, RIGHT, UP, DOWN]
            lines = LaggedStart(*[
                FadeIn(line, shift=dirs[k % 4] * 0.35, scale=1.15 if k % 2 == 0 else 0.9)
                for k, line in enumerate(q)
            ], lag_ratio=0.15)
            return seq(FadeIn(i) if i is not None else None, lines, FadeIn(a, shift=UP * 0.08) if a else None)
        if name == "archival":
            lines = LaggedStart(*[FadeIn(line, shift=DOWN * 0.05) for line in q], lag_ratio=0.14)
            return seq(FadeIn(b) if b else None, FadeIn(i, shift=LEFT * 0.15) if i is not None else None,
                       FadeIn(d) if len(d) else None, lines, FadeIn(a) if a else None)
        if name == "split":
            return AnimationGroup(FadeIn(i, shift=LEFT * 0.3) if i is not None else Wait(0),
                                  Create(d), FadeIn(q, shift=RIGHT * 0.3),
                                  FadeIn(a) if a else Wait(0), lag_ratio=0.12, run_time=run_time)
        if name == "frame":
            return seq(Create(b) if b else None, FadeIn(i) if i is not None else None, FadeIn(q, scale=0.96), FadeIn(a) if a else None)
        if name == "pull_quote":
            return seq(Create(d), FadeIn(i) if i is not None else None, FadeIn(q, scale=1.08), FadeIn(a, shift=UP * 0.08) if a else None)
        if name == "portrait_pop":
            return seq(FadeIn(i, scale=0.65) if i is not None else None, FadeIn(d, scale=0.8) if len(d) else None,
                       FadeIn(q, shift=UP * 0.12), FadeIn(a) if a else None)
        if name == "lower_third":
            return AnimationGroup(FadeIn(b, shift=UP * 0.2) if b else Wait(0),
                                  FadeIn(i, shift=RIGHT * 0.18) if i is not None else Wait(0),
                                  FadeIn(d) if len(d) else Wait(0),
                                  FadeIn(q, shift=RIGHT * 0.25), FadeIn(a, shift=RIGHT * 0.2) if a else Wait(0),
                                  lag_ratio=0.08, run_time=run_time)
        if name == "quote_marks":
            return seq(FadeIn(i) if i is not None else None, FadeIn(d, scale=1.25),
                       LaggedStart(*[FadeIn(line, shift=UP * 0.08) for line in q], lag_ratio=0.12),
                       FadeIn(a) if a else None)
        if name == "floating_card":
            return AnimationGroup(FadeIn(b, shift=UP * 0.3, scale=0.92) if b else Wait(0),
                                  FadeIn(i, shift=UP * 0.18) if i is not None else Wait(0),
                                  FadeIn(d) if len(d) else Wait(0), FadeIn(q, shift=UP * 0.18),
                                  FadeIn(a, shift=UP * 0.12) if a else Wait(0), lag_ratio=0.1, run_time=run_time)
        if name == "monochrome":
            lines = LaggedStart(*[FadeIn(line, shift=RIGHT * 0.12) for line in q], lag_ratio=0.1)
            return AnimationGroup(FadeIn(i, shift=LEFT * 0.2) if i is not None else Wait(0),
                                  FadeIn(d) if len(d) else Wait(0), lines,
                                  FadeIn(a) if a else Wait(0), lag_ratio=0.1, run_time=run_time)

        return FadeIn(self, run_time=run_time)
