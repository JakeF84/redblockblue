"""Quick sequential demo of the data-driven expression vocabulary."""

from cube_characters import *


class ExpressionLibraryDemo(CharacterScene):
    DURATION = 0.22
    HOLD = 0.18

    def construct(self):
        self.set_camera_orientation(focal_distance=1000)

        red = self.red(at=2.2 * LEFT, y_rotation=-20 * DEGREES)
        blue = self.blue(at=2.2 * RIGHT, y_rotation=20 * DEGREES)

        # A representative tour. Use red.expressions.available() to iterate
        # over all 51 presets when you want an exhaustive render.
        sequence = (
            "neutral",
            "happy",
            "excited",
            "holding_laughter",
            "smug",
            "thinking",
            "confused",
            "sceptical",
            "bored",
            "fed_up",
            "sad",
            "worried",
            "afraid",
            "terrified",
            "surprised",
            "shocked",
            "disgusted",
            "angry",
            "furious",
            "mischievous",
        )

        for name in sequence:
            self.together(
                red.expressions.animation(name, self.DURATION),
                blue.expressions.animation(name, self.DURATION),
            )
            self.wait(self.HOLD)

        self.together(
            red.expressions.neutral_animation(self.DURATION),
            blue.expressions.neutral_animation(self.DURATION),
        )
        self.wait()
