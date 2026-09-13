# RedBlockBlue Animation

Reusable block characters, quotes, and code presentations for Manim Community.
Characters express themselves through eyes, brows, mouths, gaze, and movement.

## Install and render

Use Python 3.10 or newer and install Manim's native dependencies for your platform.
Then, inside a virtual environment:

```bash
python -m pip install -e '.[dev]'
python -m manim -ql examples/semantic_character_demo.py SemanticCharacterDemo
python -m manim -ql examples/presentation_demo.py PresentationDemo
python -m pytest
```

## Characters

```python
from manim import LEFT, RIGHT
from redblockblue import RBBScene

class Demo(RBBScene):
    def construct(self):
        red = self.red(2 * LEFT)
        blue = self.blue(2 * RIGHT)

        red.react("thinking")
        red.look_at(blue)
        self.together(
            red.react_animation("happy"),
            blue.react_animation("suspicious"),
        )
        red.move_to(LEFT, duration=0.8)
        blue.spin()
```

Action methods play immediately and return the actor for chaining. Their
`*_animation()` counterparts return Manim animations for `self.play()` or
`self.together()`. Avoid animating the same facial feature twice in one play:
`react_animation()` already controls pupils, lids, brows, and mouth.

For finer control:

```python
red.eyes.squint()
red.eyebrows.cock("right")
red.mouth.smile()
red.track(blue)                  # follows a moving target
red.stop_tracking()
red.bounce()                     # idle motion
red.stop_bounce()
print(red.expressions.available())
```

Use `red.mob` for direct Manim access. Characters accept `side_length`,
`eyes_open`, `with_eyebrows`, and `with_mouth`. Arms and hand gestures have been
removed; see [MIGRATION.md](MIGRATION.md).

## Code and quotes

```python
from redblockblue import CodeStyle, CodeWindow, Quote, QuoteStyle

editor = CodeWindow(
    "def square(x):\n    return x * x",
    language="python", title="square.py", style=CodeStyle.WALKTHROUGH,
)
self.play(editor.show())
self.play(editor.focus(2))
self.play(editor.success(2))
self.play(editor.unfocus())
self.play(editor.clear_highlight())
self.play(editor.hide())

quote = Quote("Make each idea easy to follow.", style=QuoteStyle.EDITORIAL)
self.play(quote.show())
self.play(quote.hide())
```

Code line numbers start at 1. A tuple `(2, 4)` selects the inclusive range 2–4;
a list `[2, 4]` selects just those two rows. Blank interior lines count.
`CodeWindow.from_file(path)` infers language and title. Quotes accept an optional
author and an image path or Manim mobject. Call `available_styles()` on either
component to list the supported styles; strings work alongside the enums.

Build presentation actions immediately before playing them: selection methods
prepare their overlay layers. Idle bounce pauses during explicit movement.
Movement destinations and speed-based durations are resolved when the animation
is built; its starting pose is captured when playback begins.

## Layout

```text
src/redblockblue/
  scene.py                 scene factories and simultaneous playback
  core/                    targets, timing, and whole-body motion
  characters/
    actor.py               script-facing actions
    presets.py             facial expression data
    controls/              eyes, brows, mouth, expressions, motion
    rig/                   cube and face geometry; camera visibility
  presentation/            code, quotes, style specifications
src/cube_characters/       compatibility imports for older face/motion scripts
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for extension rules and
[REFACTOR_REPORT.md](REFACTOR_REPORT.md) for review findings and validation.
