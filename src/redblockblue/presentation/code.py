from __future__ import annotations

from pathlib import Path

from manim import (
    Animation,
    AnimationGroup,
    Code,
    DOWN,
    Dot,
    FadeIn,
    FadeOut,
    GRAY_B,
    GREEN_C,
    Group,
    Indicate,
    LEFT,
    LaggedStart,
    Line,
    RED_C,
    RIGHT,
    RoundedRectangle,
    Text,
    UP,
    VGroup,
    Wait,
    Wiggle,
    YELLOW,
    smooth,
)

from ..core.timing import positive_time
from ._animations import RemoveFromLayer
from .styles import CODE_STYLES, CodeStyle, style_name


class CodeWindow(Group):
    """
    Reusable, opinionated code-editor component for Manim.

    Public constructor:
        CodeWindow(code, language, title, style)

    Example:
        editor = CodeWindow(
            "def greet(name):\\n    return f'Hello {name}'",
            "python",
            "example.py",
            "clean",
        )

        self.play(editor.show())
        self.play(editor.highlight(2))
        self.play(editor.focus((1, 2)))
        self.play(editor.unfocus())
        self.play(editor.hide())

    `style` controls the entrance/presentation vibe:
        clean
        live_coding
        walkthrough
        energetic
        dramatic
        technical
    """

    STYLES = CODE_STYLES

    PANEL_FILL = "#161B22"
    PANEL_STROKE = "#30363D"
    HEADER_LINE = "#30363D"
    TITLE_COLOR = GRAY_B

    RED_BUTTON = "#FF5F56"
    AMBER_BUTTON = "#FFBD2E"
    GREEN_BUTTON = "#27C93F"

    DEFAULT_HIGHLIGHT = YELLOW
    ERROR_COLOR = RED_C
    SUCCESS_COLOR = GREEN_C

    def __init__(
        self,
        code: str,
        language: str = "python",
        title: str = "untitled",
        style: str | CodeStyle = CodeStyle.CLEAN,
    ):
        super().__init__()
        if not code.strip():
            raise ValueError("code must contain non-whitespace text")

        style = style_name(style)
        if style not in self.STYLES:
            raise ValueError(
                f"Unknown style {style!r}. "
                f"Choose from: {', '.join(self.STYLES)}"
            )

        self.source_code = code.strip("\n")
        self.language = language
        self.title_text = title
        self.style = style
        self.style_config = self.STYLES[style]

        self._active_highlights = VGroup()
        self._focused_lines = None

        self._build()

    # ==================================================================
    # CONSTRUCTION
    # ==================================================================

    def _build(self):
        self.listing = Code(
            code_string=self.source_code,
            language=self.language,
            formatter_style=self.style_config.formatter_style,
            add_line_numbers=True,
            background="rectangle",
            background_config={
                "fill_opacity": 0,
                "stroke_opacity": 0,
                "buff": 0.05,
            },
            paragraph_config={
                "font": "Monospace",
                "font_size": 23,
                "line_spacing": 0.48,
                "disable_ligatures": True,
            },
        )

        # Code/Paragraph are renderer-dependent Mobjects.  Do not address rows
        # through ``paragraph[n]``, ``len(paragraph)`` or iteration: those use
        # Mobject.split(), whose behaviour can differ once a renderer conversion
        # gives the container points of its own.  Cache the actual Paragraph row
        # submobjects once and use those everywhere.
        self._code_rows = self._paragraph_rows(self.listing.code_lines)
        self._number_rows = self._paragraph_rows(self.listing.line_numbers)

        expected_rows = len(self.source_code.split("\n"))
        if len(self._code_rows) != expected_rows:
            raise RuntimeError(
                "Manim Code row mismatch: "
                f"source has {expected_rows} rows but Code produced "
                f"{len(self._code_rows)}. "
                "This CodeWindow expects Manim Community's Paragraph-based Code."
            )

        if len(self._number_rows) != expected_rows:
            raise RuntimeError(
                "Manim Code line-number mismatch: "
                f"expected {expected_rows}, got {len(self._number_rows)}."
            )

        # Code creates its own background; this library supplies its own.
        if hasattr(self.listing, "background"):
            self.listing.remove(self.listing.background)

        max_code_width = 10.6
        max_code_height = 5.25

        if self.listing.width > max_code_width:
            self.listing.scale_to_fit_width(max_code_width)

        if self.listing.height > max_code_height:
            self.listing.scale_to_fit_height(max_code_height)

        self.header_height = 0.62
        horizontal_padding = 0.42
        bottom_padding = 0.35

        panel_width = max(
            6.2,
            self.listing.width + 2 * horizontal_padding,
        )

        panel_height = (
            self.listing.height
            + self.header_height
            + bottom_padding
            + 0.34
        )

        self.panel = RoundedRectangle(
            width=panel_width,
            height=panel_height,
            corner_radius=0.18,
            stroke_color=self.PANEL_STROKE,
            stroke_width=1.4,
            fill_color=self.PANEL_FILL,
            fill_opacity=1,
        )
        self.panel.set_z_index(0)

        header_y = self.panel.get_top()[1] - self.header_height

        self.header_separator = Line(
            [self.panel.get_left()[0] + 0.02, header_y, 0],
            [self.panel.get_right()[0] - 0.02, header_y, 0],
            stroke_color=self.HEADER_LINE,
            stroke_width=1.2,
        )
        self.header_separator.set_z_index(2)

        self.window_buttons = VGroup(
            Dot(radius=0.075, color=self.RED_BUTTON, stroke_width=0),
            Dot(radius=0.075, color=self.AMBER_BUTTON, stroke_width=0),
            Dot(radius=0.075, color=self.GREEN_BUTTON, stroke_width=0),
        ).arrange(
            RIGHT,
            buff=0.11,
        )

        self.window_buttons.move_to(
            [
                self.panel.get_left()[0] + 0.5,
                self.panel.get_top()[1] - self.header_height / 2,
                0,
            ]
        )
        self.window_buttons.set_z_index(4)

        self.title_mob = Text(
            self.title_text,
            font_size=18,
            color=self.TITLE_COLOR,
        )
        self.title_mob.move_to(
            [
                self.panel.get_center()[0],
                self.panel.get_top()[1] - self.header_height / 2,
                0,
            ]
        )
        self.title_mob.set_z_index(4)

        self.listing.next_to(
            self.header_separator,
            DOWN,
            buff=0.22,
        )
        self.listing.align_to(
            self.panel,
            LEFT,
        )
        self.listing.shift(
            RIGHT * horizontal_padding
        )
        self.listing.set_z_index(4)

        self.highlight_layer = VGroup()
        self.highlight_layer.set_z_index(3)

        # Selected row copies remain bright above the dimmed listing.
        self.focus_layer = VGroup()
        self.focus_layer.set_z_index(5)
        self._focus_overlays = VGroup()

        self.chrome = VGroup(
            self.panel,
            self.header_separator,
            self.window_buttons,
            self.title_mob,
        )

        self.add(
            self.chrome,
            self.highlight_layer,
            self.listing,
            self.focus_layer,
        )

    # ==================================================================
    # HELPERS
    # ==================================================================

    @classmethod
    def available_styles(cls):
        return tuple(cls.STYLES)

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        language: str | None = None,
        title: str | None = None,
        style: str | CodeStyle = CodeStyle.CLEAN,
    ):
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(path)

        if title is None:
            title = path.name

        if language is None:
            language = cls._language_from_suffix(path.suffix)

        return cls(
            path.read_text(encoding="utf-8"),
            language or "text",
            title,
            style,
        )

    @staticmethod
    def _language_from_suffix(suffix: str):
        return {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".json": "json",
            ".html": "html",
            ".css": "css",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".c": "c",
            ".java": "java",
            ".rs": "rust",
            ".go": "go",
            ".sql": "sql",
            ".sh": "bash",
        }.get(
            suffix.lower(),
            "text",
        )

    @staticmethod
    def _paragraph_rows(paragraph):
        """Return the real row VGroups of a Manim Paragraph.

        ``Paragraph.chars`` is documented as a VGroup containing one VGroup per
        rendered line.  Accessing it through ``.submobjects`` avoids Mobject's
        renderer-sensitive ``__getitem__`` / ``__iter__`` / ``__len__`` path.
        """
        chars = getattr(paragraph, "chars", None)
        if chars is not None and hasattr(chars, "submobjects"):
            rows = list(chars.submobjects)
            if rows:
                return rows

        # Fallback for older Manim versions.
        return list(paragraph.submobjects)

    @property
    def line_count(self):
        # Source text is the semantic authority, not Mobject.split().
        return len(self._code_rows)

    def _validate_line_number(self, n: int):
        if isinstance(n, bool) or not isinstance(n, int):
            raise TypeError(
                f"Line number must be int, got {type(n).__name__}"
            )

        if not 1 <= n <= self.line_count:
            raise ValueError(
                f"Line {n} does not exist. "
                f"This CodeWindow has {self.line_count} lines."
            )

        return n

    def _normalise_lines(self, spec):
        if isinstance(spec, int):
            values = [spec]

        elif (
            isinstance(spec, tuple)
            and len(spec) == 2
            and all(type(x) is int for x in spec)
        ):
            start, end = spec

            if end < start:
                start, end = end, start

            # Public ranges are INCLUSIVE.  (2, 4) -> 2, 3, 4.
            values = list(range(start, end + 1))

        else:
            try:
                values = list(spec)
            except TypeError as exc:
                raise TypeError(
                    "lines must be an int, (start, end), "
                    "or iterable of line numbers"
                ) from exc

        result = []
        for n in values:
            self._validate_line_number(n)
            if n not in result:
                result.append(n)

        return result

    def line(self, n: int):
        """Return exactly source row ``n`` (1-based)."""
        self._validate_line_number(n)
        return self._code_rows[n - 1]

    def lines(self, start: int, end: int | None = None):
        if end is None:
            return VGroup(self.line(start))

        return VGroup(
            *[self.line(n) for n in self._normalise_lines((start, end))]
        )

    def _line_number_mobject(self, n: int):
        self._validate_line_number(n)
        if not self._number_rows:
            return None
        return self._number_rows[n - 1]

    def _row_center_y(self, n: int):
        """Return the centre y-coordinate of logical source row ``n``."""
        number_mob = self._line_number_mobject(n)
        if number_mob is not None:
            return number_mob.get_center()[1]

        line_mob = self.line(n)
        return line_mob.get_center()[1]

    def _line_pitch(self):
        """Return one logical code-row height in scene coordinates.

        We derive this from the visible line-number rows, which exist even for
        blank source lines.  Using direct cached row submobjects keeps the result
        stable across Cairo/OpenGL and across empty code rows.
        """
        if self.line_count <= 1:
            return max(0.34, self.listing.height)

        ys = [row.get_center()[1] for row in self._number_rows]
        gaps = [
            abs(a - b)
            for a, b in zip(ys, ys[1:])
            if abs(a - b) > 1e-6
        ]

        if not gaps:
            return 0.42

        gaps.sort()
        return gaps[len(gaps) // 2]

    def _consecutive_runs(self, numbers):
        """
        Convert [1, 2, 3, 7, 8, 10] into:
            [(1, 3), (7, 8), (10, 10)]
        """
        numbers = sorted(set(numbers))

        if not numbers:
            return []

        runs = []
        start = previous = numbers[0]

        for number in numbers[1:]:
            if number == previous + 1:
                previous = number
                continue

            runs.append((start, previous))
            start = previous = number

        runs.append((start, previous))
        return runs

    def _highlight_block(
        self,
        start_line: int,
        end_line: int,
        color,
        opacity: float,
    ):
        """Create one rectangle covering an INCLUSIVE logical row range."""
        self._validate_line_number(start_line)
        self._validate_line_number(end_line)

        if end_line < start_line:
            start_line, end_line = end_line, start_line

        pitch = self._line_pitch()

        # Use the row grid directly.  This gives exactly one pitch per selected
        # row, so (1, 4) is four rows high and a single-line highlight is exactly
        # one row high.
        top = self._row_center_y(start_line) + pitch / 2
        bottom = self._row_center_y(end_line) - pitch / 2

        body_top = self.header_separator.get_center()[1] - 0.035
        body_bottom = self.panel.get_bottom()[1] + 0.08

        top = min(top, body_top)
        bottom = max(bottom, body_bottom)

        rect = RoundedRectangle(
            width=self.panel.width - 0.24,
            height=max(0.20, top - bottom),
            corner_radius=0.045,
            stroke_width=0,
            fill_color=color,
            fill_opacity=opacity,
        )
        rect.move_to(
            [
                self.panel.get_center()[0],
                (top + bottom) / 2,
                0,
            ]
        )
        rect.set_z_index(3)
        return rect

    def _highlight_rect(
        self,
        line_number: int,
        color,
        opacity: float,
    ):
        """Backward-compatible helper for a single-line highlight."""
        return self._highlight_block(
            line_number,
            line_number,
            color,
            opacity,
        )

    def _make_highlight_group(
        self,
        line_numbers,
        color,
        opacity,
    ):
        """
        Consecutive selections are merged into continuous highlight blocks.
        """
        return VGroup(
            *[
                self._highlight_block(
                    start,
                    end,
                    color,
                    opacity,
                )
                for start, end in self._consecutive_runs(line_numbers)
            ]
        )

    # ==================================================================
    # ENTRANCE / EXIT
    # ==================================================================

    def show(
        self,
        run_time: float | None = None,
    ) -> Animation:
        if run_time is None:
            run_time = self.style_config.run_time

        run_time = positive_time(run_time)
        return AnimationGroup(
            self._entrance_animation(run_time), group=self, run_time=run_time,
        )

    def _entrance_animation(self, run_time):
        def sequence(*animations):
            return AnimationGroup(*animations, lag_ratio=1, run_time=run_time)

        entrance = self.style_config.entrance

        if entrance == "clean":
            # Animate the root object, not detached child groups.  This keeps
            # highlight_layer inside the scene graph and makes hide() symmetric.
            return FadeIn(
                self,
                shift=UP * 0.05,
                run_time=run_time,
            )

        if entrance == "typing":
            glyphs = [
                glyph
                for line in self._code_rows
                for glyph in line.submobjects
            ]

            typed_code = (
                LaggedStart(
                    *[
                        FadeIn(
                            glyph,
                            shift=RIGHT * 0.015,
                        )
                        for glyph in glyphs
                    ],
                    lag_ratio=0.012,
                )
                if glyphs
                else FadeIn(self.listing.code_lines)
            )

            line_numbers = (
                FadeIn(self.listing.line_numbers)
                if hasattr(self.listing, "line_numbers")
                else Wait(0)
            )

            return sequence(
                FadeIn(
                    self.chrome,
                    shift=UP * 0.05,
                    run_time=min(
                        0.45,
                        run_time * 0.25,
                    ),
                ),
                AnimationGroup(
                    typed_code,
                    line_numbers,
                    lag_ratio=0,
                    run_time=max(
                        0.2,
                        run_time * 0.75,
                    ),
                ),
            )

        if entrance == "line_by_line":
            line_animations = [
                FadeIn(
                    line,
                    shift=RIGHT * 0.12,
                )
                for line in self._code_rows
            ]

            numbers = (
                FadeIn(self.listing.line_numbers)
                if hasattr(self.listing, "line_numbers")
                else Wait(0)
            )

            return sequence(
                FadeIn(
                    self.chrome,
                    run_time=run_time * 0.25,
                ),
                AnimationGroup(
                    numbers,
                    LaggedStart(
                        *line_animations,
                        lag_ratio=0.14,
                    ),
                    lag_ratio=0,
                    run_time=run_time * 0.75,
                ),
            )

        if entrance == "slide":
            return FadeIn(
                self,
                shift=DOWN * 0.28,
                run_time=run_time,
                rate_func=smooth,
            )

        if entrance == "dramatic":
            header_bits = VGroup(
                self.header_separator,
                self.window_buttons,
                self.title_mob,
            )

            numbers = (
                FadeIn(self.listing.line_numbers)
                if hasattr(self.listing, "line_numbers")
                else Wait(0)
            )

            return sequence(
                FadeIn(
                    self.panel,
                    scale=1.025,
                    run_time=run_time * 0.32,
                ),
                AnimationGroup(
                    AnimationGroup(*(FadeIn(part) for part in header_bits)),
                    LaggedStart(
                        *[
                            FadeIn(
                                line,
                                shift=UP * 0.08,
                            )
                            for line in self._code_rows
                        ],
                        lag_ratio=0.13,
                    ),
                    numbers,
                    lag_ratio=0.08,
                    run_time=run_time * 0.68,
                ),
            )

        if entrance == "technical":
            return FadeIn(
                self,
                shift=RIGHT * 0.06,
                run_time=run_time,
            )

        return FadeIn(
            self,
            run_time=run_time,
        )

    def hide(
        self,
        run_time: float = 0.5,
    ) -> Animation:
        return FadeOut(
            self,
            shift=DOWN * 0.08,
            run_time=positive_time(run_time),
        )

    # ==================================================================
    # SEMANTIC CODE ANIMATIONS
    # ==================================================================

    def highlight(
        self,
        lines,
        color=DEFAULT_HIGHLIGHT,
        opacity: float = 0.18,
        run_time: float = 0.35,
    ) -> Animation:
        return self._highlight_animation(lines, color, opacity, run_time)

    def _highlight_animation(self, lines, color, opacity, run_time, effect=None):
        run_time = positive_time(run_time)
        if not 0 <= opacity <= 1:
            raise ValueError("opacity must be between 0 and 1")
        numbers = self._normalise_lines(lines)
        old = list(self._active_highlights.submobjects)
        new_rects = self._make_highlight_group(numbers, color, opacity)
        self.highlight_layer.add(*new_rects.submobjects)
        self._active_highlights = new_rects
        animations = [RemoveFromLayer(rect, self.highlight_layer) for rect in old]
        animations.extend(FadeIn(rect) for rect in new_rects.submobjects)
        if effect is not None and numbers:
            animations.append(effect(VGroup(*(self.line(n) for n in numbers))))
        if not animations:
            return Wait(run_time)
        return AnimationGroup(*animations, group=self, lag_ratio=0, run_time=run_time)

    def clear_highlight(self, run_time: float = 0.25) -> Animation:
        return self._highlight_animation([], self.DEFAULT_HIGHLIGHT, 0.18, run_time)

    def focus(
        self,
        lines,
        dim_opacity: float = 0.16,
        run_time: float = 0.45,
    ) -> Animation:
        """Focus an inclusive set/range of logical source lines.

        Strategy:
        1. Dim the *whole* Manim Code mobject with one animation.
        2. Put exact copies of the selected code rows + line numbers above it.

        This avoids both fragile row-boundary masks and simultaneous per-row
        opacity animations.  ``focus((2, 4))`` therefore means exactly
        lines 2, 3 and 4.
        """
        if not 0 <= dim_opacity <= 1:
            raise ValueError("dim_opacity must be between 0 and 1")

        run_time = positive_time(run_time)
        selected_numbers = self._normalise_lines(lines)
        self._focused_lines = set(selected_numbers)

        # Remove transparent leftovers from a previous focus/unfocus cycle.
        if self.focus_layer.submobjects:
            self.focus_layer.remove(*list(self.focus_layer.submobjects))

        # Make exact, already-positioned copies of the selected rendered rows.
        # The code row and its line-number row are independent mobjects, so
        # copy both.  Blank code rows are fine because the line-number copy is
        # still visible and preserves the logical selection.
        selected_copies = VGroup()

        for number in selected_numbers:
            number_mob = self._line_number_mobject(number)
            if number_mob is not None:
                selected_copies.add(number_mob.copy())

            selected_copies.add(self.line(number).copy())

        selected_copies.set_z_index(6)
        selected_copies.set_opacity(0)

        self.focus_layer.add(selected_copies)
        self._focus_overlays = selected_copies

        return AnimationGroup(
            self.listing.animate.set_opacity(dim_opacity),
            selected_copies.animate.set_opacity(1.0),
            group=self,
            lag_ratio=0,
            run_time=run_time,
        )

    def unfocus(
        self,
        run_time: float = 0.4,
    ) -> Animation:
        """Restore the complete code listing after :meth:`focus`."""
        run_time = positive_time(run_time)
        self._focused_lines = None

        current = self._focus_overlays
        self._focus_overlays = VGroup()

        animations = [
            self.listing.animate.set_opacity(1.0),
        ]

        if current in self.focus_layer.submobjects:
            animations.append(RemoveFromLayer(current, self.focus_layer))

        return AnimationGroup(
            *animations,
            group=self,
            lag_ratio=0,
            run_time=run_time,
        )

    def indicate(
        self,
        lines,
        scale_factor: float = 1.04,
        run_time: float = 0.6,
    ) -> Animation:
        targets = VGroup(
            *[
                self.line(n)
                for n in self._normalise_lines(lines)
            ]
        )

        run_time = positive_time(run_time)
        if not targets.submobjects:
            return Wait(run_time)
        return AnimationGroup(
            Indicate(targets, scale_factor=scale_factor),
            group=self, run_time=run_time,
        )

    def error(self, lines, run_time: float = 0.55) -> Animation:
        return self._highlight_animation(
            lines, self.ERROR_COLOR, 0.22, run_time,
            effect=lambda rows: Wiggle(rows, scale_value=1.015, rotation_angle=0.015),
        )

    def success(self, lines, run_time: float = 0.45) -> Animation:
        return self._highlight_animation(
            lines, self.SUCCESS_COLOR, 0.18, run_time,
            effect=lambda rows: Indicate(rows, scale_factor=1.025),
        )
