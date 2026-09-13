from manim import *
from redblockblue import RBBScene


class SemanticCharacterDemo(RBBScene):
    def construct(self):
        red = self.red(at=2.2 * LEFT, y_rotation=-20 * DEGREES)
        blue = self.blue(at=2.2 * RIGHT, y_rotation=20 * DEGREES)

        # Narrative layer: say what the character is doing.
        red.react("thinking")
        red.look_at(blue)
        red.react("happy")

        # Primitive layer remains available when you actually want it.
        self.together(
            red.eyes.squint_animation(),
            red.eyebrows.cock_animation("right"),
            red.mouth.smile_animation(),
        )
